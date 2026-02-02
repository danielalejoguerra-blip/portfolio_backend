"""
Project API endpoints.
Public: GET endpoints (list, get by slug)
Protected: POST, PUT, DELETE endpoints (require authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_project_service, require_csrf
from app.domain.schemas.project import (
	ProjectCreate,
	ProjectListResponse,
	ProjectRead,
	ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def _entity_to_read(project) -> dict:
	"""Convert domain entity to response dict"""
	return {
		"id": project.id,
		"title": project.title,
		"slug": project.slug,
		"description": project.description,
		"content": project.content,
		"images": project.images,
		"metadata": project.metadata.to_dict(),
		"visible": project.visible,
		"order": project.order,
		"created_at": project.created_at,
		"updated_at": project.updated_at,
		"deleted_at": project.deleted_at,
	}


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.get("", response_model=ProjectListResponse)
def list_projects(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	service: ProjectService = Depends(get_project_service),
):
	"""List all published projects (public endpoint)"""
	projects, total = service.list_public_projects(limit=limit, offset=offset)
	return ProjectListResponse(
		items=[_entity_to_read(p) for p in projects],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(projects)) < total,
	)


@router.get("/{slug}", response_model=ProjectRead)
def get_project(
	slug: str,
	service: ProjectService = Depends(get_project_service),
):
	"""Get a published project by slug (public endpoint)"""
	project = service.get_public_project(slug)
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	return _entity_to_read(project)


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.get("/admin/all", response_model=ProjectListResponse)
def list_all_projects_admin(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	include_hidden: bool = Query(default=True),
	include_deleted: bool = Query(default=False),
	_current_user=Depends(get_current_user),
	service: ProjectService = Depends(get_project_service),
):
	"""List all projects including hidden/deleted (admin only)"""
	projects, total = service.list_projects(
		include_hidden=include_hidden,
		include_deleted=include_deleted,
		limit=limit,
		offset=offset,
	)
	return ProjectListResponse(
		items=[_entity_to_read(p) for p in projects],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(projects)) < total,
	)


@router.get("/admin/{project_id}", response_model=ProjectRead)
def get_project_by_id_admin(
	project_id: int,
	_current_user=Depends(get_current_user),
	service: ProjectService = Depends(get_project_service),
):
	"""Get any project by ID (admin only)"""
	project = service.get_project_by_id(project_id)
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	return _entity_to_read(project)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_csrf)])
def create_project(
	payload: ProjectCreate,
	_current_user=Depends(get_current_user),
	service: ProjectService = Depends(get_project_service),
):
	"""Create a new project (admin only)"""
	project = service.create_project(
		title=payload.title,
		slug=payload.slug,
		description=payload.description,
		content=payload.content,
		images=payload.images,
		metadata=payload.metadata,
		visible=payload.visible,
		order=payload.order,
	)
	return _entity_to_read(project)


@router.put("/{project_id}", response_model=ProjectRead, dependencies=[Depends(require_csrf)])
def update_project(
	project_id: int,
	payload: ProjectUpdate,
	_current_user=Depends(get_current_user),
	service: ProjectService = Depends(get_project_service),
):
	"""Update an existing project (admin only)"""
	try:
		project = service.update_project(
			project_id=project_id,
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

	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	return _entity_to_read(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def delete_project(
	project_id: int,
	hard: bool = Query(default=False, description="Permanently delete instead of soft delete"),
	_current_user=Depends(get_current_user),
	service: ProjectService = Depends(get_project_service),
):
	"""Delete a project (admin only). Soft delete by default."""
	deleted = service.delete_project(project_id, soft=not hard)
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


@router.post("/{project_id}/restore", response_model=ProjectRead, dependencies=[Depends(require_csrf)])
def restore_project(
	project_id: int,
	_current_user=Depends(get_current_user),
	service: ProjectService = Depends(get_project_service),
):
	"""Restore a soft-deleted project (admin only)"""
	project = service.restore_project(project_id)
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	return _entity_to_read(project)
