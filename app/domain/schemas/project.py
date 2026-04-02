"""
Project Pydantic schemas for request/response validation.
"""
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
	completed = "completed"
	in_progress = "in_progress"
	maintained = "maintained"
	archived = "archived"


class ProjectCategory(str, Enum):
	web = "web"
	mobile = "mobile"
	api = "api"
	cli = "cli"
	data = "data"
	devops = "devops"
	game = "game"
	other = "other"


# ---------------------------------------------------------------------------
# Nested value-object schemas
# ---------------------------------------------------------------------------

class TechnologyItem(BaseModel):
	"""A single technology used in a project."""
	name: str = Field(min_length=1, max_length=100)
	category: str = Field(
		min_length=1, max_length=50,
		description="backend | frontend | database | devops | mobile | other",
	)
	icon_url: Optional[str] = Field(None, max_length=2048)
	version: Optional[str] = Field(None, max_length=50)
	proficiency: Optional[str] = Field(
		None,
		description="beginner | intermediate | advanced | expert",
	)


class ProjectMetric(BaseModel):
	"""A measurable project achievement / KPI."""
	label: str = Field(min_length=1, max_length=100)
	value: str = Field(min_length=1, max_length=100)
	icon_url: Optional[str] = Field(None, max_length=2048)


class ProjectFeature(BaseModel):
	"""A notable feature of the project."""
	title: str = Field(min_length=1, max_length=255)
	description: Optional[str] = Field(None, max_length=500)
	icon_url: Optional[str] = Field(None, max_length=2048)


class ProjectChallenge(BaseModel):
	"""A technical challenge and how it was solved."""
	challenge: str = Field(min_length=1, max_length=500)
	solution: str = Field(min_length=1, max_length=500)


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
	"""Schema for creating a new project."""
	title: str = Field(min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	# Classification
	status: ProjectStatus = ProjectStatus.completed
	category: Optional[ProjectCategory] = None
	role: Optional[str] = Field(None, max_length=255)

	# Timeline
	start_date: Optional[date] = None
	end_date: Optional[date] = None

	# Collaboration
	team_size: Optional[int] = Field(None, ge=1)
	client: Optional[str] = Field(None, max_length=255)

	# Tech stack
	tech_stack: list[TechnologyItem] = Field(default_factory=list)

	# Links
	project_url: Optional[str] = Field(None, max_length=2048)
	repository_url: Optional[str] = Field(None, max_length=2048)
	documentation_url: Optional[str] = Field(None, max_length=2048)
	case_study_url: Optional[str] = Field(None, max_length=2048)

	# Highlights
	metrics: list[ProjectMetric] = Field(default_factory=list)
	features: list[ProjectFeature] = Field(default_factory=list)
	challenges: list[ProjectChallenge] = Field(default_factory=list)

	# Media & display
	images: list[str] = Field(default_factory=list)
	featured: bool = False
	visible: bool = True
	order: int = Field(default=0, ge=0)

	metadata: dict[str, Any] = Field(default_factory=dict)
	translations: dict[str, dict[str, str]] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
	"""Schema for updating an existing project."""
	title: Optional[str] = Field(None, min_length=1, max_length=255)
	slug: Optional[str] = Field(
		None, min_length=1, max_length=255,
		pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
	)
	description: Optional[str] = Field(None, max_length=1000)
	content: Optional[str] = None

	status: Optional[ProjectStatus] = None
	category: Optional[ProjectCategory] = None
	role: Optional[str] = Field(None, max_length=255)

	start_date: Optional[date] = None
	end_date: Optional[date] = None

	team_size: Optional[int] = Field(None, ge=1)
	client: Optional[str] = Field(None, max_length=255)

	tech_stack: Optional[list[TechnologyItem]] = None

	project_url: Optional[str] = Field(None, max_length=2048)
	repository_url: Optional[str] = Field(None, max_length=2048)
	documentation_url: Optional[str] = Field(None, max_length=2048)
	case_study_url: Optional[str] = Field(None, max_length=2048)

	metrics: Optional[list[ProjectMetric]] = None
	features: Optional[list[ProjectFeature]] = None
	challenges: Optional[list[ProjectChallenge]] = None

	images: Optional[list[str]] = None
	featured: Optional[bool] = None
	visible: Optional[bool] = None
	order: Optional[int] = Field(None, ge=0)

	metadata: Optional[dict[str, Any]] = None
	translations: Optional[dict[str, dict[str, str]]] = None


# ---------------------------------------------------------------------------
# Read schema
# ---------------------------------------------------------------------------

class ProjectRead(BaseModel):
	"""Full project response schema."""
	id: int
	title: str
	slug: str
	description: Optional[str] = None
	content: Optional[str] = None

	status: ProjectStatus
	category: Optional[ProjectCategory] = None
	role: Optional[str] = None

	start_date: Optional[date] = None
	end_date: Optional[date] = None

	team_size: Optional[int] = None
	client: Optional[str] = None

	tech_stack: list[dict[str, Any]] = Field(default_factory=list)

	project_url: Optional[str] = None
	repository_url: Optional[str] = None
	documentation_url: Optional[str] = None
	case_study_url: Optional[str] = None

	metrics: list[dict[str, Any]] = Field(default_factory=list)
	features: list[dict[str, Any]] = Field(default_factory=list)
	challenges: list[dict[str, Any]] = Field(default_factory=list)

	images: list[str] = Field(default_factory=list)
	featured: bool = False
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

class ProjectListParams(BaseModel):
	"""Query parameters for listing projects."""
	limit: int = Field(default=20, ge=1, le=100)
	offset: int = Field(default=0, ge=0)
	include_hidden: bool = False
	include_deleted: bool = False
	status: Optional[ProjectStatus] = None
	category: Optional[ProjectCategory] = None
	featured_only: bool = False


class ProjectListResponse(BaseModel):
	"""Paginated project list response."""
	items: list[ProjectRead]
	total: int
	limit: int
	offset: int
	has_more: bool

