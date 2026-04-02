"""
Education Pydantic schemas for request/response validation.
"""
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class DegreeType(str, Enum):
	bachelor = "bachelor"
	master = "master"
	phd = "phd"
	associate = "associate"
	bootcamp = "bootcamp"
	certification = "certification"
	online_course = "online_course"
	high_school = "high_school"
	other = "other"


# ---------------------------------------------------------------------------
# Nested value-object schemas
# ---------------------------------------------------------------------------

class ActivityItem(BaseModel):
	"""Extracurricular activity / student organisation membership."""
	name: str = Field(min_length=1, max_length=255)
	role: Optional[str] = Field(None, max_length=255)
	description: Optional[str] = Field(None, max_length=500)


class AchievementItem(BaseModel):
	"""Academic award or notable honour."""
	title: str = Field(min_length=1, max_length=255)
	year: Optional[int] = Field(None, ge=1900, le=2100)
	description: Optional[str] = Field(None, max_length=500)


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class EducationCreate(BaseModel):
	"""Schema for creating a new education entry."""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	# Institution
	institution: str = Field(min_length=1, max_length=255)
	institution_url: Optional[str] = Field(None, max_length=2048)
	location: Optional[str] = Field(None, max_length=255)

	# Programme
	degree_type: DegreeType = DegreeType.bachelor
	field_of_study: Optional[str] = Field(None, max_length=255)
	start_date: Optional[date] = None
	end_date: Optional[date] = None

	# Credential
	credential_id: Optional[str] = Field(None, max_length=255)
	credential_url: Optional[str] = Field(None, max_length=2048)
	grade: Optional[str] = Field(None, max_length=50)
	honors: Optional[str] = Field(None, max_length=255)

	# Academic extras
	relevant_coursework: list[str] = Field(default_factory=list)
	activities: list[ActivityItem] = Field(default_factory=list)
	achievements: list[AchievementItem] = Field(default_factory=list)

	# Media & display
	images: list[str] = Field(default_factory=list)
	visible: bool = True
	order: int = Field(default=0, ge=0)

	metadata: dict[str, Any] = Field(default_factory=dict)
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)

	@field_validator("end_date")
	@classmethod
	def end_after_start(cls, v: Optional[date], info: Any) -> Optional[date]:
		start = info.data.get("start_date")
		if v and start and v < start:
			raise ValueError("end_date must be on or after start_date")
		return v


class EducationUpdate(BaseModel):
	"""Schema for updating an existing education entry."""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	institution: Optional[str] = Field(None, min_length=1, max_length=255)
	institution_url: Optional[str] = Field(None, max_length=2048)
	location: Optional[str] = Field(None, max_length=255)

	degree_type: Optional[DegreeType] = None
	field_of_study: Optional[str] = Field(None, max_length=255)
	start_date: Optional[date] = None
	end_date: Optional[date] = None

	credential_id: Optional[str] = Field(None, max_length=255)
	credential_url: Optional[str] = Field(None, max_length=2048)
	grade: Optional[str] = Field(None, max_length=50)
	honors: Optional[str] = Field(None, max_length=255)

	relevant_coursework: Optional[list[str]] = None
	activities: Optional[list[ActivityItem]] = None
	achievements: Optional[list[AchievementItem]] = None

	images: Optional[list[str]] = None
	visible: Optional[bool] = None
	order: Optional[int] = Field(None, ge=0)

	metadata: Optional[dict[str, Any]] = None
	translations: Optional[dict[str, dict[str, str]]] = None


# ---------------------------------------------------------------------------
# Read schema
# ---------------------------------------------------------------------------

class EducationRead(BaseModel):
	"""Full education response schema."""
	id: int
	title: str
	slug: str
	description: Optional[str] = None
	content: Optional[str] = None

	institution: str
	institution_url: Optional[str] = None
	location: Optional[str] = None

	degree_type: DegreeType
	field_of_study: Optional[str] = None
	start_date: Optional[date] = None
	end_date: Optional[date] = None
	is_ongoing: bool = False

	credential_id: Optional[str] = None
	credential_url: Optional[str] = None
	grade: Optional[str] = None
	honors: Optional[str] = None

	relevant_coursework: list[str] = Field(default_factory=list)
	activities: list[dict[str, Any]] = Field(default_factory=list)
	achievements: list[dict[str, Any]] = Field(default_factory=list)

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

class EducationListParams(BaseModel):
	"""Query parameters for listing education entries."""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False
	degree_type: Optional[DegreeType] = None


class EducationListResponse(BaseModel):
	"""Paginated education list response."""
	items: list[EducationRead]
	total: int
	limit: int
	offset: int
	has_more: bool

