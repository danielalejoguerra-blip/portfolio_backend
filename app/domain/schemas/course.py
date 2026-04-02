"""
Course Pydantic schemas for request/response validation.
"""
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class CourseLevel(str, Enum):
	beginner = "beginner"
	intermediate = "intermediate"
	advanced = "advanced"
	expert = "expert"


class CourseCategory(str, Enum):
	backend = "backend"
	frontend = "frontend"
	mobile = "mobile"
	devops = "devops"
	data = "data"
	design = "design"
	security = "security"
	cloud = "cloud"
	soft_skills = "soft_skills"
	other = "other"


# ---------------------------------------------------------------------------
# Nested value-object schemas
# ---------------------------------------------------------------------------

class SkillGained(BaseModel):
	"""A skill learned during the course."""
	name: str = Field(min_length=1, max_length=100)
	category: Optional[str] = Field(None, max_length=50)


class SyllabusSection(BaseModel):
	"""A section / module of the course syllabus."""
	title: str = Field(min_length=1, max_length=255)
	topics: list[str] = Field(default_factory=list)
	duration_minutes: Optional[int] = Field(None, ge=0)


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class CourseCreate(BaseModel):
	"""Schema for creating a new course or certification."""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	# Classification
	is_certification: bool = False
	category: Optional[CourseCategory] = None
	level: Optional[CourseLevel] = None

	# Platform
	platform: Optional[str] = Field(None, max_length=255)
	platform_url: Optional[str] = Field(None, max_length=2048)
	instructor: Optional[str] = Field(None, max_length=255)
	instructor_url: Optional[str] = Field(None, max_length=2048)

	# Timeline
	completion_date: Optional[date] = None
	expiration_date: Optional[date] = None
	duration_hours: Optional[int] = Field(None, ge=1)

	# Credential
	credential_id: Optional[str] = Field(None, max_length=255)
	certificate_url: Optional[str] = Field(None, max_length=2048)
	certificate_image_url: Optional[str] = Field(None, max_length=2048)
	badge_url: Optional[str] = Field(None, max_length=2048)

	# Learning outcomes
	skills_gained: list[SkillGained] = Field(default_factory=list)
	syllabus: list[SyllabusSection] = Field(default_factory=list)

	# Media & display
	images: list[str] = Field(default_factory=list)
	visible: bool = True
	order: int = Field(default=0, ge=0)

	metadata: dict[str, Any] = Field(default_factory=dict)
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)


class CourseUpdate(BaseModel):
	"""Schema for updating an existing course or certification."""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	is_certification: Optional[bool] = None
	category: Optional[CourseCategory] = None
	level: Optional[CourseLevel] = None

	platform: Optional[str] = Field(None, max_length=255)
	platform_url: Optional[str] = Field(None, max_length=2048)
	instructor: Optional[str] = Field(None, max_length=255)
	instructor_url: Optional[str] = Field(None, max_length=2048)

	completion_date: Optional[date] = None
	expiration_date: Optional[date] = None
	duration_hours: Optional[int] = Field(None, ge=1)

	credential_id: Optional[str] = Field(None, max_length=255)
	certificate_url: Optional[str] = Field(None, max_length=2048)
	certificate_image_url: Optional[str] = Field(None, max_length=2048)
	badge_url: Optional[str] = Field(None, max_length=2048)

	skills_gained: Optional[list[SkillGained]] = None
	syllabus: Optional[list[SyllabusSection]] = None

	images: Optional[list[str]] = None
	visible: Optional[bool] = None
	order: Optional[int] = Field(None, ge=0)

	metadata: Optional[dict[str, Any]] = None
	translations: Optional[dict[str, dict[str, str]]] = None


# ---------------------------------------------------------------------------
# Read schema
# ---------------------------------------------------------------------------

class CourseRead(BaseModel):
	"""Full course response schema."""
	id: int
	title: str
	slug: str
	description: Optional[str] = None
	content: Optional[str] = None

	is_certification: bool = False
	category: Optional[CourseCategory] = None
	level: Optional[CourseLevel] = None

	platform: Optional[str] = None
	platform_url: Optional[str] = None
	instructor: Optional[str] = None
	instructor_url: Optional[str] = None

	completion_date: Optional[date] = None
	expiration_date: Optional[date] = None
	duration_hours: Optional[int] = None
	is_expired: bool = False

	credential_id: Optional[str] = None
	certificate_url: Optional[str] = None
	certificate_image_url: Optional[str] = None
	badge_url: Optional[str] = None

	skills_gained: list[dict[str, Any]] = Field(default_factory=list)
	syllabus: list[dict[str, Any]] = Field(default_factory=list)

	images: list[str] = Field(default_factory=list)
	visible: bool
	order: int

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

class CourseListParams(BaseModel):
	"""Query parameters for listing courses."""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False
	certifications_only: bool = False
	category: Optional[CourseCategory] = None
	level: Optional[CourseLevel] = None


class CourseListResponse(BaseModel):
	"""Paginated course list response."""
	items: list[CourseRead]
	total: int
	limit: int
	offset: int
	has_more: bool

