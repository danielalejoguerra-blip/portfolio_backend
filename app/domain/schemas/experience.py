"""
Experience Pydantic schemas for request/response validation.
"""
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class EmploymentType(str, Enum):
	full_time = "full_time"
	part_time = "part_time"
	contract = "contract"
	freelance = "freelance"
	internship = "internship"
	volunteer = "volunteer"


class WorkMode(str, Enum):
	on_site = "on_site"
	remote = "remote"
	hybrid = "hybrid"


# ---------------------------------------------------------------------------
# Nested value-object schemas
# ---------------------------------------------------------------------------

class TechStackItem(BaseModel):
	"""A single technology used during this role."""
	name: str = Field(min_length=1, max_length=100)
	category: str = Field(
		min_length=1, max_length=50,
		description="backend | frontend | database | devops | mobile | other",
	)
	icon_url: Optional[str] = Field(None, max_length=2048)
	version: Optional[str] = Field(None, max_length=50)


class AchievementItem(BaseModel):
	"""A measurable professional achievement."""
	label: str = Field(min_length=1, max_length=255)
	value: str = Field(min_length=1, max_length=255)
	icon_url: Optional[str] = Field(None, max_length=2048)


class RelatedProject(BaseModel):
	"""Reference to a project built during this role."""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(None, max_length=255)
	url: Optional[str] = Field(None, max_length=2048)


class ReferenceItem(BaseModel):
	"""Professional reference contact."""
	name: str = Field(min_length=1, max_length=255)
	role: Optional[str] = Field(None, max_length=255)
	linkedin_url: Optional[str] = Field(None, max_length=2048)
	available: bool = True


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class ExperienceCreate(BaseModel):
	"""Schema for creating a new experience entry."""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	# Company
	company: str = Field(min_length=1, max_length=255)
	company_url: Optional[str] = Field(None, max_length=2048)
	company_logo_url: Optional[str] = Field(None, max_length=2048)
	location: Optional[str] = Field(None, max_length=255)

	# Role details
	employment_type: EmploymentType = EmploymentType.full_time
	work_mode: Optional[WorkMode] = None
	department: Optional[str] = Field(None, max_length=255)

	# Timeline
	start_date: date
	end_date: Optional[date] = None
	is_current: bool = False

	# Tech stack
	tech_stack: list[TechStackItem] = Field(default_factory=list)

	# Highlights
	responsibilities: list[str] = Field(default_factory=list)
	achievements: list[AchievementItem] = Field(default_factory=list)
	related_projects: list[RelatedProject] = Field(default_factory=list)

	# References
	references: list[ReferenceItem] = Field(default_factory=list)

	# Media & display
	images: list[str] = Field(default_factory=list)
	visible: bool = True
	order: int = Field(default=0, ge=0)

	metadata: dict[str, Any] = Field(default_factory=dict)
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)

	@model_validator(mode="after")
	def validate_dates(self) -> "ExperienceCreate":
		if self.is_current and self.end_date:
			raise ValueError("end_date must be empty when is_current is True")
		if not self.is_current and self.end_date and self.end_date < self.start_date:
			raise ValueError("end_date must be on or after start_date")
		return self


class ExperienceUpdate(BaseModel):
	"""Schema for updating an existing experience entry."""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	company: Optional[str] = Field(None, min_length=1, max_length=255)
	company_url: Optional[str] = Field(None, max_length=2048)
	company_logo_url: Optional[str] = Field(None, max_length=2048)
	location: Optional[str] = Field(None, max_length=255)

	employment_type: Optional[EmploymentType] = None
	work_mode: Optional[WorkMode] = None
	department: Optional[str] = Field(None, max_length=255)

	start_date: Optional[date] = None
	end_date: Optional[date] = None
	is_current: Optional[bool] = None

	tech_stack: Optional[list[TechStackItem]] = None

	responsibilities: Optional[list[str]] = None
	achievements: Optional[list[AchievementItem]] = None
	related_projects: Optional[list[RelatedProject]] = None

	references: Optional[list[ReferenceItem]] = None

	images: Optional[list[str]] = None
	visible: Optional[bool] = None
	order: Optional[int] = Field(None, ge=0)

	metadata: Optional[dict[str, Any]] = None
	translations: Optional[dict[str, dict[str, str]]] = None


# ---------------------------------------------------------------------------
# Read schema
# ---------------------------------------------------------------------------

class ExperienceRead(BaseModel):
	"""Full experience response schema."""
	id: int
	title: str
	slug: str
	description: Optional[str] = None
	content: Optional[str] = None

	company: str
	company_url: Optional[str] = None
	company_logo_url: Optional[str] = None
	location: Optional[str] = None

	employment_type: EmploymentType
	work_mode: Optional[WorkMode] = None
	department: Optional[str] = None

	start_date: date
	end_date: Optional[date] = None
	is_current: bool = False

	tech_stack: list[dict[str, Any]] = Field(default_factory=list)

	responsibilities: list[str] = Field(default_factory=list)
	achievements: list[dict[str, Any]] = Field(default_factory=list)
	related_projects: list[dict[str, Any]] = Field(default_factory=list)

	references: list[dict[str, Any]] = Field(default_factory=list)

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

class ExperienceListParams(BaseModel):
	"""Query parameters for listing experience entries."""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False
	current_only: bool = False
	employment_type: Optional[EmploymentType] = None


class ExperienceListResponse(BaseModel):
	"""Paginated experience list response."""
	items: list[ExperienceRead]
	total: int
	limit: int
	offset: int
	has_more: bool
