"""
Shared Pydantic schemas for content domains.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ContentMetadataSchema(BaseModel):
	"""Flexible metadata schema - accepts any JSON structure"""
	data: dict[str, Any] = Field(default_factory=dict)

	class Config:
		from_attributes = True


class PaginationParams(BaseModel):
	"""Common pagination parameters"""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)


class PaginatedResponse(BaseModel):
	"""Generic paginated response wrapper"""
	items: list[Any]
	total: int
	limit: int
	offset: int
	has_more: bool


class ContentListParams(BaseModel):
	"""Common list query parameters for admin views"""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False
