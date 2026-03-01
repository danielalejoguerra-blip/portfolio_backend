"""
Skills API endpoints.
Public: GET endpoints (list, get by slug)
Protected: POST, PUT, DELETE endpoints (require authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_skill_service, require_csrf
from app.domain.schemas.skill import (
	SkillCreate,
	SkillListResponse,
	SkillRead,
	SkillUpdate,
)
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["skills"])


def _entity_to_read(skill) -> dict:
	"""Convert domain entity to response dict"""
	return {
		"id": skill.id,
		"title": skill.title,
		"slug": skill.slug,
		"description": skill.description,
		"metadata": skill.metadata.to_dict(),
		"visible": skill.visible,
		"order": skill.order,
		"created_at": skill.created_at,
		"updated_at": skill.updated_at,
		"deleted_at": skill.deleted_at,
	}


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.get("", response_model=SkillListResponse)
def list_skills(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	service: SkillService = Depends(get_skill_service),
):
	"""List all published skills (public endpoint)"""
	skills, total = service.list_public_skills(limit=limit, offset=offset)
	return SkillListResponse(
		items=[_entity_to_read(s) for s in skills],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(skills)) < total,
	)


@router.get("/{slug}", response_model=SkillRead)
def get_skill(
	slug: str,
	service: SkillService = Depends(get_skill_service),
):
	"""Get a published skill by slug (public endpoint)"""
	skill = service.get_public_skill(slug)
	if not skill:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
	return _entity_to_read(skill)


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.get("/admin/all", response_model=SkillListResponse)
def list_all_skills_admin(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	include_hidden: bool = Query(default=True),
	include_deleted: bool = Query(default=False),
	_current_user=Depends(get_current_user),
	service: SkillService = Depends(get_skill_service),
):
	"""List all skills including hidden/deleted (admin only)"""
	skills, total = service.list_skills(
		include_hidden=include_hidden,
		include_deleted=include_deleted,
		limit=limit,
		offset=offset,
	)
	return SkillListResponse(
		items=[_entity_to_read(s) for s in skills],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(skills)) < total,
	)


@router.get("/admin/{skill_id}", response_model=SkillRead)
def get_skill_by_id_admin(
	skill_id: int,
	_current_user=Depends(get_current_user),
	service: SkillService = Depends(get_skill_service),
):
	"""Get any skill by ID (admin only)"""
	skill = service.get_skill_by_id(skill_id)
	if not skill:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
	return _entity_to_read(skill)


@router.post("", response_model=SkillRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_csrf)])
def create_skill(
	payload: SkillCreate,
	_current_user=Depends(get_current_user),
	service: SkillService = Depends(get_skill_service),
):
	"""Create a new skill (admin only)"""
	skill = service.create_skill(
		title=payload.title,
		slug=payload.slug,
		description=payload.description,
		metadata=payload.metadata,
		visible=payload.visible,
		order=payload.order,
	)
	return _entity_to_read(skill)


@router.put("/{skill_id}", response_model=SkillRead, dependencies=[Depends(require_csrf)])
def update_skill(
	skill_id: int,
	payload: SkillUpdate,
	_current_user=Depends(get_current_user),
	service: SkillService = Depends(get_skill_service),
):
	"""Update an existing skill (admin only)"""
	try:
		skill = service.update_skill(
			skill_id=skill_id,
			title=payload.title,
			slug=payload.slug,
			description=payload.description,
			metadata=payload.metadata,
			visible=payload.visible,
			order=payload.order,
		)
	except ValueError as e:
		if "slug" in str(e):
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

	if not skill:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
	return _entity_to_read(skill)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def delete_skill(
	skill_id: int,
	hard: bool = Query(default=False, description="Permanently delete instead of soft delete"),
	_current_user=Depends(get_current_user),
	service: SkillService = Depends(get_skill_service),
):
	"""Delete a skill (admin only). Soft delete by default."""
	deleted = service.delete_skill(skill_id, soft=not hard)
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")


@router.post("/{skill_id}/restore", response_model=SkillRead, dependencies=[Depends(require_csrf)])
def restore_skill(
	skill_id: int,
	_current_user=Depends(get_current_user),
	service: SkillService = Depends(get_skill_service),
):
	"""Restore a soft-deleted skill (admin only)"""
	skill = service.restore_skill(skill_id)
	if not skill:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
	return _entity_to_read(skill)
