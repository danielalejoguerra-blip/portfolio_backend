"""
Education Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class EducationCreate(BaseModel):
	"""Schema for creating a new education entry"""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None
	images: list[str] = Field(default_factory=list)
	metadata: dict[str, Any] = Field(default_factory=dict)
	visible: bool = True
	order: int = Field(default=0, ge=0)


class EducationUpdate(BaseModel):
	"""Schema for updating an existing education entry"""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None
	images: Optional[list[str]] = None
	metadata: Optional[dict[str, Any]] = None
	visible: Optional[bool] = None
	order: Optional[int] = Field(None, ge=0)


class EducationRead(BaseModel):
	"""Schema for education response"""
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

	class Config:
		from_attributes = True


class EducationListParams(BaseModel):
	"""Query parameters for listing education entries"""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False


class EducationListResponse(BaseModel):
	"""Paginated education list response"""
	items: list[EducationRead]
	total: int
	limit: int
	offset: int
	has_more: bool
