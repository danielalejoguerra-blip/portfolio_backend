"""
Courses API endpoints.
Public: GET endpoints (list, get by slug)
Protected: POST, PUT, DELETE endpoints (require authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_course_service, get_current_user, require_csrf
from app.domain.schemas.course import (
	CourseCreate,
	CourseListResponse,
	CourseRead,
	CourseUpdate,
)
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


def _entity_to_read(course) -> dict:
	"""Convert domain entity to response dict"""
	return {
		"id": course.id,
		"title": course.title,
		"slug": course.slug,
		"description": course.description,
		"content": course.content,
		"images": course.images,
		"metadata": course.metadata.to_dict(),
		"visible": course.visible,
		"order": course.order,
		"created_at": course.created_at,
		"updated_at": course.updated_at,
		"deleted_at": course.deleted_at,
	}


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.get("", response_model=CourseListResponse)
def list_courses(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	service: CourseService = Depends(get_course_service),
):
	"""List all published courses (public endpoint)"""
	courses, total = service.list_public_courses(limit=limit, offset=offset)
	return CourseListResponse(
		items=[_entity_to_read(c) for c in courses],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(courses)) < total,
	)


@router.get("/{slug}", response_model=CourseRead)
def get_course(
	slug: str,
	service: CourseService = Depends(get_course_service),
):
	"""Get a published course by slug (public endpoint)"""
	course = service.get_public_course(slug)
	if not course:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
	return _entity_to_read(course)


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.get("/admin/all", response_model=CourseListResponse)
def list_all_courses_admin(
	limit: int = Query(default=20, ge=1, le=100),
	offset: int = Query(default=0, ge=0),
	include_hidden: bool = Query(default=True),
	include_deleted: bool = Query(default=False),
	_current_user=Depends(get_current_user),
	service: CourseService = Depends(get_course_service),
):
	"""List all courses including hidden/deleted (admin only)"""
	courses, total = service.list_courses(
		include_hidden=include_hidden,
		include_deleted=include_deleted,
		limit=limit,
		offset=offset,
	)
	return CourseListResponse(
		items=[_entity_to_read(c) for c in courses],
		total=total,
		limit=limit,
		offset=offset,
		has_more=(offset + len(courses)) < total,
	)


@router.get("/admin/{course_id}", response_model=CourseRead)
def get_course_by_id_admin(
	course_id: int,
	_current_user=Depends(get_current_user),
	service: CourseService = Depends(get_course_service),
):
	"""Get any course by ID (admin only)"""
	course = service.get_course_by_id(course_id)
	if not course:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
	return _entity_to_read(course)


@router.post("", response_model=CourseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_csrf)])
def create_course(
	payload: CourseCreate,
	_current_user=Depends(get_current_user),
	service: CourseService = Depends(get_course_service),
):
	"""Create a new course (admin only)"""
	course = service.create_course(
		title=payload.title,
		slug=payload.slug,
		description=payload.description,
		content=payload.content,
		images=payload.images,
		metadata=payload.metadata,
		visible=payload.visible,
		order=payload.order,
	)
	return _entity_to_read(course)


@router.put("/{course_id}", response_model=CourseRead, dependencies=[Depends(require_csrf)])
def update_course(
	course_id: int,
	payload: CourseUpdate,
	_current_user=Depends(get_current_user),
	service: CourseService = Depends(get_course_service),
):
	"""Update an existing course (admin only)"""
	try:
		course = service.update_course(
			course_id=course_id,
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

	if not course:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
	return _entity_to_read(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def delete_course(
	course_id: int,
	hard: bool = Query(default=False, description="Permanently delete instead of soft delete"),
	_current_user=Depends(get_current_user),
	service: CourseService = Depends(get_course_service),
):
	"""Delete a course (admin only). Soft delete by default."""
	deleted = service.delete_course(course_id, soft=not hard)
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


@router.post("/{course_id}/restore", response_model=CourseRead, dependencies=[Depends(require_csrf)])
def restore_course(
	course_id: int,
	_current_user=Depends(get_current_user),
	service: CourseService = Depends(get_course_service),
):
	"""Restore a soft-deleted course (admin only)"""
	course = service.restore_course(course_id)
	if not course:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
	return _entity_to_read(course)
