"""
Personal info API endpoints.
Public: GET endpoints (list, get by id)
Protected: POST, PUT, DELETE endpoints (require authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_language, get_personal_info_service, require_csrf
from app.core.i18n import resolve_translation
from app.domain.schemas.personal_info import (
	PersonalInfoCreate,
	PersonalInfoListResponse,
	PersonalInfoRead,
	PersonalInfoUpdate,
)
from app.services.personal_info_service import PersonalInfoService

router = APIRouter(prefix="/personal-info", tags=["personal-info"])


def _entity_to_read(info, lang: str = "es") -> dict:
	"""Convert domain entity to response dict"""
	data = {
		"id": info.id,
		"full_name": info.full_name,
		"headline": info.headline,
		"bio": info.bio,
		"email": info.email,
		"phone": info.phone,
		"location": info.location,
		"website": info.website,
		"avatar_url": info.avatar_url,
		"resume_url": info.resume_url,
		"social_links": info.social_links,
		"metadata": info.metadata.to_dict(),
		"visible": info.visible,
		"order": info.order,
		"created_at": info.created_at,
		"updated_at": info.updated_at,
		"deleted_at": info.deleted_at,
		"translations": info.translations,
		"lang": lang,
	}
	return resolve_translation(data, info.translations, lang, ["headline", "bio"])


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.get("", response_model=PersonalInfoListResponse)
def list_personal_info(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	lang: str = Depends(get_language),
	service: PersonalInfoService = Depends(get_personal_info_service),
):
	"""List all published personal info entries (public endpoint)"""
	items, total = service.list_public_personal_info(limit=limit, offset=offset)
	return PersonalInfoListResponse(
		items=[_entity_to_read(i, lang=lang) for i in items],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(items)) < total,
	)


@router.get("/{info_id}", response_model=PersonalInfoRead)
def get_personal_info(
	info_id: int,
	lang: str = Depends(get_language),
	service: PersonalInfoService = Depends(get_personal_info_service),
):
	"""Get a published personal info entry by ID (public endpoint)"""
	info = service.get_public_personal_info(info_id)
	if not info:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personal info not found")
	return _entity_to_read(info, lang=lang)


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.get("/admin/all", response_model=PersonalInfoListResponse)
def list_all_personal_info_admin(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	include_hidden: bool = Query(default=True),
	include_deleted: bool = Query(default=False),
	lang: str = Depends(get_language),
	_current_user=Depends(get_current_user),
	service: PersonalInfoService = Depends(get_personal_info_service),
):
	"""List all personal info entries including hidden/deleted (admin only)"""
	items, total = service.list_personal_info(
		include_hidden=include_hidden,
		include_deleted=include_deleted,
		limit=limit,
		offset=offset,
	)
	return PersonalInfoListResponse(
		items=[_entity_to_read(i, lang=lang) for i in items],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(items)) < total,
	)


@router.get("/admin/{info_id}", response_model=PersonalInfoRead)
def get_personal_info_by_id_admin(
	info_id: int,
	lang: str = Depends(get_language),
	_current_user=Depends(get_current_user),
	service: PersonalInfoService = Depends(get_personal_info_service),
):
	"""Get any personal info entry by ID (admin only)"""
	info = service.get_personal_info_by_id(info_id)
	if not info:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personal info not found")
	return _entity_to_read(info, lang=lang)


@router.post("", response_model=PersonalInfoRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_csrf)])
def create_personal_info(
	payload: PersonalInfoCreate,
	_current_user=Depends(get_current_user),
	service: PersonalInfoService = Depends(get_personal_info_service),
):
	"""Create a new personal info entry (admin only)"""
	info = service.create_personal_info(
		full_name=payload.full_name,
		headline=payload.headline,
		bio=payload.bio,
		email=payload.email,
		phone=payload.phone,
		location=payload.location,
		website=payload.website,
		avatar_url=payload.avatar_url,
		resume_url=payload.resume_url,
		social_links=payload.social_links,
		metadata=payload.metadata,
		visible=payload.visible,
		order=payload.order,
		translations=payload.translations,
	)
	return _entity_to_read(info, lang="es")


@router.put("/{info_id}", response_model=PersonalInfoRead, dependencies=[Depends(require_csrf)])
def update_personal_info(
	info_id: int,
	payload: PersonalInfoUpdate,
	_current_user=Depends(get_current_user),
	service: PersonalInfoService = Depends(get_personal_info_service),
):
	"""Update an existing personal info entry (admin only)"""
	info = service.update_personal_info(
		info_id=info_id,
		full_name=payload.full_name,
		headline=payload.headline,
		bio=payload.bio,
		email=payload.email,
		phone=payload.phone,
		location=payload.location,
		website=payload.website,
		avatar_url=payload.avatar_url,
		resume_url=payload.resume_url,
		social_links=payload.social_links,
		metadata=payload.metadata,
		visible=payload.visible,
		order=payload.order,
		translations=payload.translations,
	)
	if not info:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personal info not found")
	return _entity_to_read(info, lang="es")


@router.delete("/{info_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def delete_personal_info(
	info_id: int,
	hard: bool = Query(default=False, description="Permanently delete instead of soft delete"),
	_current_user=Depends(get_current_user),
	service: PersonalInfoService = Depends(get_personal_info_service),
):
	"""Delete a personal info entry (admin only). Soft delete by default."""
	deleted = service.delete_personal_info(info_id, soft=not hard)
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personal info not found")


@router.post("/{info_id}/restore", response_model=PersonalInfoRead, dependencies=[Depends(require_csrf)])
def restore_personal_info(
	info_id: int,
	_current_user=Depends(get_current_user),
	service: PersonalInfoService = Depends(get_personal_info_service),
):
	"""Restore a soft-deleted personal info entry (admin only)"""
	info = service.restore_personal_info(info_id)
	if not info:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personal info not found")
	return _entity_to_read(info, lang="es")
