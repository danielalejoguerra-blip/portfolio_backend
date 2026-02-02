"""
Experience API endpoints.
Public: GET endpoints (list, get by slug)
Protected: POST, PUT, DELETE endpoints (require authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_experience_service, require_csrf
from app.domain.schemas.experience import (
	ExperienceCreate,
	ExperienceListResponse,
	ExperienceRead,
	ExperienceUpdate,
)
from app.services.experience_service import ExperienceService

router = APIRouter(prefix="/experience", tags=["experience"])


def _entity_to_read(experience) -> dict:
	"""Convert domain entity to response dict"""
	return {
		"id": experience.id,
		"title": experience.title,
		"slug": experience.slug,
		"description": experience.description,
		"content": experience.content,
		"images": experience.images,
		"metadata": experience.metadata.to_dict(),
		"visible": experience.visible,
		"order": experience.order,
		"created_at": experience.created_at,
		"updated_at": experience.updated_at,
		"deleted_at": experience.deleted_at,
	}


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.get("", response_model=ExperienceListResponse)
def list_experiences(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	service: ExperienceService = Depends(get_experience_service),
):
	"""List all published experiences (public endpoint)"""
	experiences, total = service.list_public_experiences(limit=limit, offset=offset)
	return ExperienceListResponse(
		items=[_entity_to_read(e) for e in experiences],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(experiences)) < total,
	)


@router.get("/{slug}", response_model=ExperienceRead)
def get_experience(
	slug: str,
	service: ExperienceService = Depends(get_experience_service),
):
	"""Get a published experience by slug (public endpoint)"""
	experience = service.get_public_experience(slug)
	if not experience:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
	return _entity_to_read(experience)


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.get("/admin/all", response_model=ExperienceListResponse)
def list_all_experiences_admin(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	include_hidden: bool = Query(default=True),
	include_deleted: bool = Query(default=False),
	_current_user=Depends(get_current_user),
	service: ExperienceService = Depends(get_experience_service),
):
	"""List all experiences including hidden/deleted (admin only)"""
	experiences, total = service.list_experiences(
		include_hidden=include_hidden,
		include_deleted=include_deleted,
		limit=limit,
		offset=offset,
	)
	return ExperienceListResponse(
		items=[_entity_to_read(e) for e in experiences],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(experiences)) < total,
	)


@router.get("/admin/{experience_id}", response_model=ExperienceRead)
def get_experience_by_id_admin(
	experience_id: int,
	_current_user=Depends(get_current_user),
	service: ExperienceService = Depends(get_experience_service),
):
	"""Get any experience by ID (admin only)"""
	experience = service.get_experience_by_id(experience_id)
	if not experience:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
	return _entity_to_read(experience)


@router.post("", response_model=ExperienceRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_csrf)])
def create_experience(
	payload: ExperienceCreate,
	_current_user=Depends(get_current_user),
	service: ExperienceService = Depends(get_experience_service),
):
	"""Create a new experience (admin only)"""
	experience = service.create_experience(
		title=payload.title,
		slug=payload.slug,
		description=payload.description,
		content=payload.content,
		images=payload.images,
		metadata=payload.metadata,
		visible=payload.visible,
		order=payload.order,
	)
	return _entity_to_read(experience)


@router.put("/{experience_id}", response_model=ExperienceRead, dependencies=[Depends(require_csrf)])
def update_experience(
	experience_id: int,
	payload: ExperienceUpdate,
	_current_user=Depends(get_current_user),
	service: ExperienceService = Depends(get_experience_service),
):
	"""Update an existing experience (admin only)"""
	try:
		experience = service.update_experience(
			experience_id=experience_id,
			title=payload.title,
			slug=payload.slug,
			description=payload.description,
			content=payload.content,
			images=payload.images,
			metadata=payload.metadata,
			visible=payload.visible,
			order=payload.order,
		)
	except ValueError as e:
		if "slug" in str(e):
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

	if not experience:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
	return _entity_to_read(experience)


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def delete_experience(
	experience_id: int,
	hard: bool = Query(default=False, description="Permanently delete instead of soft delete"),
	_current_user=Depends(get_current_user),
	service: ExperienceService = Depends(get_experience_service),
):
	"""Delete an experience (admin only). Soft delete by default."""
	deleted = service.delete_experience(experience_id, soft=not hard)
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")


@router.post("/{experience_id}/restore", response_model=ExperienceRead, dependencies=[Depends(require_csrf)])
def restore_experience(
	experience_id: int,
	_current_user=Depends(get_current_user),
	service: ExperienceService = Depends(get_experience_service),
):
	"""Restore a soft-deleted experience (admin only)"""
	experience = service.restore_experience(experience_id)
	if not experience:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
	return _entity_to_read(experience)
