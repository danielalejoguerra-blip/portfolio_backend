"""
Course Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
	"""Schema for creating a new course"""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None
	images: list[str] = Field(default_factory=list)
	metadata: dict[str, Any] = Field(default_factory=dict)
	visible: bool = True
	order: int = Field(default=0, ge=0)
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)


class CourseUpdate(BaseModel):
	"""Schema for updating an existing course"""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None
	images: Optional[list[str]] = None
	metadata: Optional[dict[str, Any]] = None
	visible: Optional[bool] = None
	order: Optional[int] = Field(None, ge=0)
	translations: Optional[dict[str, dict[str, str]]] = None


class CourseRead(BaseModel):
	"""Schema for course response"""
	id: int
	title: str
	slug: str
	description: Optional[str] = None
	content: Optional[str] = None
	images: list[str] = Field(default_factory=list)
	metadata: dict[str, Any] = Field(default_factory=dict)
	visible: bool
	order: int
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)
	lang: str = "es"

	class Config:
		from_attributes = True


class CourseListParams(BaseModel):
	"""Query parameters for listing courses"""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False


class CourseListResponse(BaseModel):
	"""Paginated course list response"""
	items: list[CourseRead]
	total: int
	limit: int
	offset: int
	has_more: bool
