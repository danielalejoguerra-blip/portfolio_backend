"""
Experience API endpoints.
Public: GET endpoints (list, get by slug)
Protected: POST, PUT, DELETE endpoints (require authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_experience_service, get_language, require_csrf
from app.core.i18n import resolve_translation
from app.domain.schemas.experience import (
	ExperienceCreate,
	ExperienceListResponse,
	ExperienceRead,
	ExperienceUpdate,
)
from app.services.experience_service import ExperienceService

router = APIRouter(prefix="/experience", tags=["experience"])


def _entity_to_read(experience, lang: str = "es") -> dict:
	"""Convert domain entity to response dict"""
	data = {
		"id": experience.id,
		"title": experience.title,
		"slug": experience.slug,
		"description": experience.description,
		"content": experience.content,
		"company": experience.company,
		"company_url": experience.company_url,
		"company_logo_url": experience.company_logo_url,
		"location": experience.location,
		"employment_type": experience.employment_type,
		"work_mode": experience.work_mode,
		"department": experience.department,
		"start_date": experience.start_date,
		"end_date": experience.end_date,
		"is_current": experience.is_current,
		"tech_stack": experience.tech_stack,
		"responsibilities": experience.responsibilities,
		"achievements": experience.achievements,
		"related_projects": experience.related_projects,
		"references": experience.references,
		"images": experience.images,
		"metadata": experience.metadata.to_dict(),
		"visible": experience.visible,
		"order": experience.order,
		"created_at": experience.created_at,
		"updated_at": experience.updated_at,
		"deleted_at": experience.deleted_at,
		"translations": experience.translations,
		"lang": lang,
	}
	return resolve_translation(data, experience.translations, lang, ["title", "description", "content"])


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.get("", response_model=ExperienceListResponse)
def list_experiences(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	lang: str = Depends(get_language),
	service: ExperienceService = Depends(get_experience_service),
):
	"""List all published experiences (public endpoint)"""
	experiences, total = service.list_public_experiences(limit=limit, offset=offset)
	return ExperienceListResponse(
		items=[_entity_to_read(e, lang=lang) for e in experiences],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(experiences)) < total,
	)


@router.get("/{slug}", response_model=ExperienceRead)
def get_experience(
	slug: str,
	lang: str = Depends(get_language),
	service: ExperienceService = Depends(get_experience_service),
):
	"""Get a published experience by slug (public endpoint)"""
	experience = service.get_public_experience(slug)
	if not experience:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
	return _entity_to_read(experience, lang=lang)


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.get("/admin/all", response_model=ExperienceListResponse)
def list_all_experiences_admin(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	include_hidden: bool = Query(default=True),
	include_deleted: bool = Query(default=False),
	lang: str = Depends(get_language),
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
		items=[_entity_to_read(e, lang=lang) for e in experiences],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(experiences)) < total,
	)


@router.get("/admin/{experience_id}", response_model=ExperienceRead)
def get_experience_by_id_admin(
	experience_id: int,
	lang: str = Depends(get_language),
	_current_user=Depends(get_current_user),
	service: ExperienceService = Depends(get_experience_service),
):
	"""Get any experience by ID (admin only)"""
	experience = service.get_experience_by_id(experience_id)
	if not experience:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
	return _entity_to_read(experience, lang=lang)


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
		company=payload.company or "",
		company_url=payload.company_url,
		company_logo_url=payload.company_logo_url,
		location=payload.location,
		employment_type=payload.employment_type or "full_time",
		work_mode=payload.work_mode,
		department=payload.department,
		start_date=payload.start_date,
		end_date=payload.end_date,
		is_current=payload.is_current or False,
		tech_stack=[t.model_dump() for t in payload.tech_stack] if payload.tech_stack else None,
		responsibilities=payload.responsibilities,
		achievements=[a.model_dump() for a in payload.achievements] if payload.achievements else None,
		related_projects=[r.model_dump() for r in payload.related_projects] if payload.related_projects else None,
		references=[r.model_dump() for r in payload.references] if payload.references else None,
		images=payload.images,
		metadata=payload.metadata,
		visible=payload.visible,
		order=payload.order,
		translations=payload.translations,
	)
	return _entity_to_read(experience, lang="es")


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
			company=payload.company,
			company_url=payload.company_url,
			company_logo_url=payload.company_logo_url,
			location=payload.location,
			employment_type=payload.employment_type,
			work_mode=payload.work_mode,
			department=payload.department,
			start_date=payload.start_date,
			end_date=payload.end_date,
			is_current=payload.is_current,
			tech_stack=[t.model_dump() for t in payload.tech_stack] if payload.tech_stack else None,
			responsibilities=payload.responsibilities,
			achievements=[a.model_dump() for a in payload.achievements] if payload.achievements else None,
			related_projects=[r.model_dump() for r in payload.related_projects] if payload.related_projects else None,
			references=[r.model_dump() for r in payload.references] if payload.references else None,
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

	if not experience:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
	return _entity_to_read(experience, lang="es")


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
	return _entity_to_read(experience, lang="es")
