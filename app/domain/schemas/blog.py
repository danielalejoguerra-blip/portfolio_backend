"""
Blog Pydantic schemas for request/response validation.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class BlogPostStatus(str, Enum):
	"""Publication status of a blog post.

	- draft:     Not visible in the public site.
	- published: Visible immediately.
	- scheduled: Will be published at the indicated date (published_at).
	"""
	draft = "draft"
	published = "published"
	scheduled = "scheduled"


class BlogPostCreate(BaseModel):
	"""Schema for creating a new blog post"""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None
	images: list[str] = Field(default_factory=list)
	metadata: dict[str, Any] = Field(default_factory=dict)
	status: BlogPostStatus = BlogPostStatus.draft
	published_at: Optional[datetime] = None  # Required when status=scheduled
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)

	@model_validator(mode="after")
	def validate_scheduled(self) -> "BlogPostCreate":
		if self.status == BlogPostStatus.scheduled and not self.published_at:
			raise ValueError("published_at is required when status is 'scheduled'")
		return self


class BlogPostUpdate(BaseModel):
	"""Schema for updating an existing blog post"""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None
	images: Optional[list[str]] = None
	metadata: Optional[dict[str, Any]] = None
	status: Optional[BlogPostStatus] = None
	published_at: Optional[datetime] = None  # Required when status=scheduled
	translations: Optional[dict[str, dict[str, str]]] = None

	@model_validator(mode="after")
	def validate_scheduled(self) -> "BlogPostUpdate":
		if self.status == BlogPostStatus.scheduled and not self.published_at:
			raise ValueError("published_at is required when status is 'scheduled'")
		return self


class BlogPostRead(BaseModel):
	"""Schema for blog post response"""
	id: int
	title: str
	slug: str
	description: Optional[str] = None
	content: Optional[str] = None
	images: list[str] = Field(default_factory=list)
	metadata: dict[str, Any] = Field(default_factory=dict)
	status: BlogPostStatus = BlogPostStatus.draft
	published_at: Optional[datetime] = None
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)
	lang: str = "es"

	class Config:
		from_attributes = True


class BlogPostListParams(BaseModel):
	"""Query parameters for listing blog posts"""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False
	include_scheduled: bool = False  # Include future-dated posts


class BlogPostListResponse(BaseModel):
	"""Paginated blog post list response"""
	items: list[BlogPostRead]
	total: int
	limit: int
	offset: int
	has_more: bool
