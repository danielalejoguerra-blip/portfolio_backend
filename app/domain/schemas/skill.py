"""
Skill Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class SkillCreate(BaseModel):
	"""Schema for creating a new skill"""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	metadata: dict[str, Any] = Field(default_factory=dict)
	visible: bool = True
	order: int = Field(default=0, ge=0)


class SkillUpdate(BaseModel):
	"""Schema for updating an existing skill"""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	metadata: Optional[dict[str, Any]] = None
	visible: Optional[bool] = None
	order: Optional[int] = Field(None, ge=0)


class SkillRead(BaseModel):
	"""Schema for skill response"""
	id: int
	title: str
	slug: str
	description: Optional[str] = None
	metadata: dict[str, Any] = Field(default_factory=dict)
	visible: bool
	order: int
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None

	class Config:
		from_attributes = True


class SkillListParams(BaseModel):
	"""Query parameters for listing skills"""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False


class SkillListResponse(BaseModel):
	"""Paginated skill list response"""
	items: list[SkillRead]
	total: int
	limit: int
	offset: int
	has_more: bool
