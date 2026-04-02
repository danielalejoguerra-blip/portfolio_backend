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


class ImagePosition(str, Enum):
	"""CSS-equivalent object-position / float position for images."""
	inline = "inline"       # Full-width inside the article flow
	left = "left"           # Floated left with text wrap
	right = "right"         # Floated right with text wrap
	center = "center"       # Centred, narrower than full-width
	background = "background"  # Used as a section background


class CalloutType(str, Enum):
	info = "info"
	warning = "warning"
	tip = "tip"
	danger = "danger"


class BlockType(str, Enum):
	text = "text"
	image = "image"
	gallery = "gallery"
	code = "code"
	callout = "callout"
	video = "video"
	divider = "divider"
	quote = "quote"


# ---------------------------------------------------------------------------
# Nested value-object schemas
# ---------------------------------------------------------------------------

class GalleryImageItem(BaseModel):
	"""A single image inside a gallery block."""
	url: str = Field(min_length=1, max_length=2048)
	alt: Optional[str] = Field(None, max_length=255)
	caption: Optional[str] = Field(None, max_length=500)


class ContentBlock(BaseModel):
	"""
	A single editorial block within a blog post.

	Only the fields relevant to ``block_type`` need to be filled:
	  text    →  content
	  image   →  image_url, image_position, image_alt, caption
	  gallery →  gallery_items
	  code    →  content, language
	  callout →  content, callout_type
	  video   →  video_url, caption
	  quote   →  content, caption (attribution)
	  divider →  (no extra fields needed)
	"""
	block_type: BlockType
	content: Optional[str] = None
	image_url: Optional[str] = Field(None, max_length=2048)
	image_position: ImagePosition = ImagePosition.inline
	image_alt: Optional[str] = Field(None, max_length=255)
	caption: Optional[str] = Field(None, max_length=500)
	language: Optional[str] = Field(None, max_length=50)
	callout_type: Optional[CalloutType] = None
	video_url: Optional[str] = Field(None, max_length=2048)
	gallery_items: list[GalleryImageItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class BlogPostCreate(BaseModel):
	"""Schema for creating a new blog post."""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	# Structured content (preferred over plain ``content``)
	content_blocks: list[ContentBlock] = Field(default_factory=list)

	# Cover image
	cover_image_url: Optional[str] = Field(None, max_length=2048)
	cover_image_alt: Optional[str] = Field(None, max_length=255)
	cover_image_position: ImagePosition = ImagePosition.center

	# Classification
	category: Optional[str] = Field(None, max_length=100)
	tags: list[str] = Field(default_factory=list)
	series: Optional[str] = Field(None, max_length=255)
	series_order: Optional[int] = Field(None, ge=1)

	# Reading experience
	reading_time_minutes: Optional[int] = Field(None, ge=1, le=300)
	featured: bool = False

	# SEO
	seo_title: Optional[str] = Field(None, max_length=60)
	seo_description: Optional[str] = Field(None, max_length=160)
	canonical_url: Optional[str] = Field(None, max_length=2048)
	og_image_url: Optional[str] = Field(None, max_length=2048)

	# Media & publishing
	images: list[str] = Field(default_factory=list)
	status: BlogPostStatus = BlogPostStatus.draft
	published_at: Optional[datetime] = None

	metadata: dict[str, Any] = Field(default_factory=dict)
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)

	@model_validator(mode="after")
	def validate_scheduled(self) -> "BlogPostCreate":
		if self.status == BlogPostStatus.scheduled and not self.published_at:
			raise ValueError("published_at is required when status is 'scheduled'")
		return self


class BlogPostUpdate(BaseModel):
	"""Schema for updating an existing blog post."""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	content_blocks: Optional[list[ContentBlock]] = None

	cover_image_url: Optional[str] = Field(None, max_length=2048)
	cover_image_alt: Optional[str] = Field(None, max_length=255)
	cover_image_position: Optional[ImagePosition] = None

	category: Optional[str] = Field(None, max_length=100)
	tags: Optional[list[str]] = None
	series: Optional[str] = Field(None, max_length=255)
	series_order: Optional[int] = Field(None, ge=1)

	reading_time_minutes: Optional[int] = Field(None, ge=1, le=300)
	featured: Optional[bool] = None

	seo_title: Optional[str] = Field(None, max_length=60)
	seo_description: Optional[str] = Field(None, max_length=160)
	canonical_url: Optional[str] = Field(None, max_length=2048)
	og_image_url: Optional[str] = Field(None, max_length=2048)

	images: Optional[list[str]] = None
	status: Optional[BlogPostStatus] = None
	published_at: Optional[datetime] = None

	metadata: Optional[dict[str, Any]] = None
	translations: Optional[dict[str, dict[str, str]]] = None

	@model_validator(mode="after")
	def validate_scheduled(self) -> "BlogPostUpdate":
		if self.status == BlogPostStatus.scheduled and not self.published_at:
			raise ValueError("published_at is required when status is 'scheduled'")
		return self


# ---------------------------------------------------------------------------
# Read schema
# ---------------------------------------------------------------------------

class BlogPostRead(BaseModel):
	"""Full blog post response schema."""
	id: int
	title: str
	slug: str
	description: Optional[str] = None
	content: Optional[str] = None
	content_blocks: list[dict[str, Any]] = Field(default_factory=list)

	cover_image_url: Optional[str] = None
	cover_image_alt: Optional[str] = None
	cover_image_position: str = "center"

	category: Optional[str] = None
	tags: list[str] = Field(default_factory=list)
	series: Optional[str] = None
	series_order: Optional[int] = None

	reading_time_minutes: Optional[int] = None
	featured: bool = False

	seo_title: Optional[str] = None
	seo_description: Optional[str] = None
	canonical_url: Optional[str] = None
	og_image_url: Optional[str] = None

	images: list[str] = Field(default_factory=list)
	status: BlogPostStatus = BlogPostStatus.draft
	published_at: Optional[datetime] = None

	metadata: dict[str, Any] = Field(default_factory=dict)
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)
	lang: str = "es"

	class Config:
		from_attributes = True


# ---------------------------------------------------------------------------
# List helpers
# ---------------------------------------------------------------------------

class BlogPostListParams(BaseModel):
	"""Query parameters for listing blog posts."""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False
	include_scheduled: bool = False
	category: Optional[str] = None
	tag: Optional[str] = None
	series: Optional[str] = None
	featured_only: bool = False


class BlogPostListResponse(BaseModel):
	"""Paginated blog post list response."""
	items: list[BlogPostRead]
	total: int
	limit: int
	offset: int
	has_more: bool

