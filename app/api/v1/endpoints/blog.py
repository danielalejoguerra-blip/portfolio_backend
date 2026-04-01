"""
Blog API endpoints.
Public: GET endpoints (list, get by slug)
Protected: POST, PUT, DELETE endpoints (require authentication)
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_blog_service, get_current_user, get_language, require_csrf
from app.core.i18n import resolve_translation
from app.domain.schemas.blog import (
	BlogPostCreate,
	BlogPostListResponse,
	BlogPostRead,
	BlogPostStatus,
	BlogPostUpdate,
)
from app.infrastructure.realtime.socket_server import emit_blog_event
from app.services.blog_service import BlogService

router = APIRouter(prefix="/blog", tags=["blog"])


def _entity_to_read(post, lang: str = "es") -> dict:
	"""Convert domain entity to response dict"""
	data = {
		"id": post.id,
		"title": post.title,
		"slug": post.slug,
		"description": post.description,
		"content": post.content,
		"images": post.images,
		"metadata": post.metadata.to_dict(),
		"status": post.status,
		"published_at": post.published_at,
		"created_at": post.created_at,
		"updated_at": post.updated_at,
		"deleted_at": post.deleted_at,
		"translations": post.translations,
		"lang": lang,
	}
	return resolve_translation(data, post.translations, lang, ["title", "description", "content"])


def _status_to_db_fields(status_value: BlogPostStatus, published_at=None):
	"""Translate API status into (visible, published_at) for the DB layer."""
	if status_value == BlogPostStatus.draft:
		return False, None
	if status_value == BlogPostStatus.published:
		return True, datetime.now(timezone.utc)
	# scheduled
	return True, published_at


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.get("", response_model=BlogPostListResponse)
def list_posts(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	lang: str = Depends(get_language),
	service: BlogService = Depends(get_blog_service),
):
	"""List all published blog posts (public endpoint)"""
	posts, total = service.list_public_posts(limit=limit, offset=offset)
	return BlogPostListResponse(
		items=[_entity_to_read(p, lang=lang) for p in posts],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(posts)) < total,
	)


@router.get("/{slug}", response_model=BlogPostRead)
def get_post(
	slug: str,
	lang: str = Depends(get_language),
	service: BlogService = Depends(get_blog_service),
):
	"""Get a published blog post by slug (public endpoint)"""
	post = service.get_public_post(slug)
	if not post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
	return _entity_to_read(post, lang=lang)


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.get("/admin/all", response_model=BlogPostListResponse)
def list_all_posts_admin(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	include_hidden: bool = Query(default=True),
	include_deleted: bool = Query(default=False),
	include_scheduled: bool = Query(default=True),
	lang: str = Depends(get_language),
	_current_user=Depends(get_current_user),
	service: BlogService = Depends(get_blog_service),
):
	"""List all blog posts including hidden/deleted/scheduled (admin only)"""
	posts, total = service.list_posts(
		include_hidden=include_hidden,
		include_deleted=include_deleted,
		include_scheduled=include_scheduled,
		limit=limit,
		offset=offset,
	)
	return BlogPostListResponse(
		items=[_entity_to_read(p, lang=lang) for p in posts],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(posts)) < total,
	)


@router.get("/admin/{post_id}", response_model=BlogPostRead)
def get_post_by_id_admin(
	post_id: int,
	lang: str = Depends(get_language),
	_current_user=Depends(get_current_user),
	service: BlogService = Depends(get_blog_service),
):
	"""Get any blog post by ID (admin only)"""
	post = service.get_post_by_id(post_id)
	if not post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
	return _entity_to_read(post, lang=lang)


@router.post("", response_model=BlogPostRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_csrf)])
async def create_post(
	payload: BlogPostCreate,
	_current_user=Depends(get_current_user),
	service: BlogService = Depends(get_blog_service),
):
	"""Create a new blog post (admin only)"""
	visible, published_at = _status_to_db_fields(payload.status, payload.published_at)
	post = service.create_post(
		title=payload.title,
		slug=payload.slug,
		description=payload.description,
		content=payload.content,
		images=payload.images,
		metadata=payload.metadata,
		visible=visible,
		published_at=published_at,
		translations=payload.translations,
	)
	data = _entity_to_read(post, lang="es")
	await emit_blog_event("blog:created", data)
	if post.status == "published":
		await emit_blog_event("blog:published", data)
	elif post.status == "scheduled":
		await emit_blog_event("blog:scheduled", data)
	return data


@router.put("/{post_id}", response_model=BlogPostRead, dependencies=[Depends(require_csrf)])
async def update_post(
	post_id: int,
	payload: BlogPostUpdate,
	_current_user=Depends(get_current_user),
	service: BlogService = Depends(get_blog_service),
):
	"""Update an existing blog post (admin only)"""
	# Resolve visible/published_at from status if provided
	visible = None
	published_at = payload.published_at
	if payload.status is not None:
		visible, published_at = _status_to_db_fields(payload.status, payload.published_at)

	# Fetch previous status to detect transitions
	existing = service.get_post_by_id(post_id)
	if not existing:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
	previous_status = existing.status

	try:
		post = service.update_post(
			post_id=post_id,
			title=payload.title,
			slug=payload.slug,
			description=payload.description,
			content=payload.content,
			images=payload.images,
			metadata=payload.metadata,
			visible=visible,
			published_at=published_at,
			translations=payload.translations,
		)
	except ValueError as e:
		if "slug" in str(e):
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

	if not post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

	data = _entity_to_read(post, lang="es")
	await emit_blog_event("blog:updated", data)
	if post.status == "published" and previous_status != "published":
		await emit_blog_event("blog:published", data)
	elif post.status == "scheduled" and previous_status != "scheduled":
		await emit_blog_event("blog:scheduled", data)
	return data


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
async def delete_post(
	post_id: int,
	hard: bool = Query(default=False, description="Permanently delete instead of soft delete"),
	_current_user=Depends(get_current_user),
	service: BlogService = Depends(get_blog_service),
):
	"""Delete a blog post (admin only). Soft delete by default."""
	deleted = service.delete_post(post_id, soft=not hard)
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
	await emit_blog_event("blog:deleted", {"id": post_id, "hard": hard})


@router.post("/{post_id}/restore", response_model=BlogPostRead, dependencies=[Depends(require_csrf)])
async def restore_post(
	post_id: int,
	_current_user=Depends(get_current_user),
	service: BlogService = Depends(get_blog_service),
):
	"""Restore a soft-deleted blog post (admin only)"""
	post = service.restore_post(post_id)
	if not post:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
	data = _entity_to_read(post, lang="es")
	await emit_blog_event("blog:restored", data)
	return data
