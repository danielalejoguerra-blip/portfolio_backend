"""
Experience Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ExperienceCreate(BaseModel):
	"""Schema for creating a new experience entry"""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None
	images: list[str] = Field(default_factory=list)
	metadata: dict[str, Any] = Field(default_factory=dict)
	visible: bool = True
	order: int = Field(default=0, ge=0)


class ExperienceUpdate(BaseModel):
	"""Schema for updating an existing experience entry"""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None
	images: Optional[list[str]] = None
	metadata: Optional[dict[str, Any]] = None
	visible: Optional[bool] = None
	order: Optional[int] = Field(None, ge=0)


class ExperienceRead(BaseModel):
	"""Schema for experience response"""
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


class ExperienceListParams(BaseModel):
	"""Query parameters for listing experience entries"""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False


class ExperienceListResponse(BaseModel):
	"""Paginated experience list response"""
	items: list[ExperienceRead]
	total: int
	limit: int
	offset: int
	has_more: bool
