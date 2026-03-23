"""
Education API endpoints.
Public: GET endpoints (list, get by slug)
Protected: POST, PUT, DELETE endpoints (require authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_education_service, get_language, require_csrf
from app.core.i18n import resolve_translation
from app.domain.schemas.education import (
	EducationCreate,
	EducationListResponse,
	EducationRead,
	EducationUpdate,
)
from app.services.education_service import EducationService

router = APIRouter(prefix="/education", tags=["education"])


def _entity_to_read(education, lang: str = "es") -> dict:
	"""Convert domain entity to response dict"""
	data = {
		"id": education.id,
		"title": education.title,
		"slug": education.slug,
		"description": education.description,
		"content": education.content,
		"images": education.images,
		"metadata": education.metadata.to_dict(),
		"visible": education.visible,
		"order": education.order,
		"created_at": education.created_at,
		"updated_at": education.updated_at,
		"deleted_at": education.deleted_at,
		"translations": education.translations,
		"lang": lang,
	}
	return resolve_translation(data, education.translations, lang, ["description", "content"])


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.get("", response_model=EducationListResponse)
def list_education(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	lang: str = Depends(get_language),
	service: EducationService = Depends(get_education_service),
):
	"""List all published education entries (public endpoint)"""
	entries, total = service.list_public_education(limit=limit, offset=offset)
	return EducationListResponse(
		items=[_entity_to_read(e, lang=lang) for e in entries],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(entries)) < total,
	)


@router.get("/{slug}", response_model=EducationRead)
def get_education(
	slug: str,
	lang: str = Depends(get_language),
	service: EducationService = Depends(get_education_service),
):
	"""Get a published education entry by slug (public endpoint)"""
	education = service.get_public_education(slug)
	if not education:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")
	return _entity_to_read(education, lang=lang)


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.get("/admin/all", response_model=EducationListResponse)
def list_all_education_admin(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	include_hidden: bool = Query(default=True),
	include_deleted: bool = Query(default=False),
	lang: str = Depends(get_language),
	_current_user=Depends(get_current_user),
	service: EducationService = Depends(get_education_service),
):
	"""List all education entries including hidden/deleted (admin only)"""
	entries, total = service.list_education(
		include_hidden=include_hidden,
		include_deleted=include_deleted,
		limit=limit,
		offset=offset,
	)
	return EducationListResponse(
		items=[_entity_to_read(e, lang=lang) for e in entries],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(entries)) < total,
	)


@router.get("/admin/{education_id}", response_model=EducationRead)
def get_education_by_id_admin(
	education_id: int,
	lang: str = Depends(get_language),
	_current_user=Depends(get_current_user),
	service: EducationService = Depends(get_education_service),
):
	"""Get any education entry by ID (admin only)"""
	education = service.get_education_by_id(education_id)
	if not education:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")
	return _entity_to_read(education, lang=lang)


@router.post("", response_model=EducationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_csrf)])
def create_education(
	payload: EducationCreate,
	_current_user=Depends(get_current_user),
	service: EducationService = Depends(get_education_service),
):
	"""Create a new education entry (admin only)"""
	education = service.create_education(
		title=payload.title,
		slug=payload.slug,
		description=payload.description,
		content=payload.content,
		images=payload.images,
		metadata=payload.metadata,
		visible=payload.visible,
		order=payload.order,
		translations=payload.translations,
	)
	return _entity_to_read(education, lang="es")


@router.put("/{education_id}", response_model=EducationRead, dependencies=[Depends(require_csrf)])
def update_education(
	education_id: int,
	payload: EducationUpdate,
	_current_user=Depends(get_current_user),
	service: EducationService = Depends(get_education_service),
):
	"""Update an existing education entry (admin only)"""
	try:
		education = service.update_education(
			education_id=education_id,
			title=payload.title,
			slug=payload.slug,
			description=payload.description,
			content=payload.content,
			images=payload.images,
			metadata=payload.metadata,
			visible=payload.visible,
			order=payload.order,
			translations=payload.translations,
		)
	except ValueError as e:
		if "slug" in str(e):
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

	if not education:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")
	return _entity_to_read(education, lang="es")


@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def delete_education(
	education_id: int,
	hard: bool = Query(default=False, description="Permanently delete instead of soft delete"),
	_current_user=Depends(get_current_user),
	service: EducationService = Depends(get_education_service),
):
	"""Delete an education entry (admin only). Soft delete by default."""
	deleted = service.delete_education(education_id, soft=not hard)
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")


@router.post("/{education_id}/restore", response_model=EducationRead, dependencies=[Depends(require_csrf)])
def restore_education(
	education_id: int,
	_current_user=Depends(get_current_user),
	service: EducationService = Depends(get_education_service),
):
	"""Restore a soft-deleted education entry (admin only)"""
	education = service.restore_education(education_id)
	if not education:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")
	return _entity_to_read(education, lang="es")
