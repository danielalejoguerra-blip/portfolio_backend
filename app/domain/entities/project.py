"""
Project entity for portfolio projects domain.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class TechnologyItem:
	"""
	Value object describing a single technology used in a project.

	``category`` groups the tech for display (backend, frontend, devops, …).
	``proficiency`` is optional and can be used for hover tooltips.
	"""
	name: str
	category: str                  # backend | frontend | database | devops | mobile | other
	icon_url: Optional[str] = None # URL to SVG/PNG icon
	version: Optional[str] = None  # e.g. "3.11", "18.x"
	proficiency: Optional[str] = None  # beginner | intermediate | advanced | expert


@dataclass(frozen=True)
class ProjectMetric:
	"""A single measurable achievement for a project (e.g. '10 k+ users')."""
	label: str
	value: str
	icon_url: Optional[str] = None


@dataclass(frozen=True)
class Project:
	"""
	Project entity representing a portfolio project.

	First-class fields cover every detail a professional portfolio entry needs.
	The ``metadata`` field is reserved for arbitrary extras.

	Status values: completed | in_progress | maintained | archived.
	Category values: web | mobile | api | cli | data | devops | game | other.
	"""
	# ── Identity ─────────────────────────────────────────────────────────────
	id: int
	title: str
	slug: str
	description: Optional[str]     # Short public-facing summary (≤ 300 chars)
	content: Optional[str]         # Long-form case-study content (Markdown)

	# ── Classification ───────────────────────────────────────────────────────
	status: str                    # completed | in_progress | maintained | archived
	category: Optional[str]        # web | mobile | api | cli | data | devops | …
	role: Optional[str]            # Lead Developer | Contributor | Architect | …

	# ── Timeline ─────────────────────────────────────────────────────────────
	start_date: Optional[date]
	end_date: Optional[date]       # None when status = in_progress / maintained

	# ── Collaboration ────────────────────────────────────────────────────────
	team_size: Optional[int]       # 1 = solo; None = unknown
	client: Optional[str]          # External client / company name if applicable

	# ── Tech stack ───────────────────────────────────────────────────────────
	# Structured list: [{"name": "FastAPI", "category": "backend", "icon_url": …}]
	tech_stack: list[dict[str, Any]]

	# ── Links ────────────────────────────────────────────────────────────────
	project_url: Optional[str]     # Live demo / production URL
	repository_url: Optional[str]  # GitHub / GitLab / Bitbucket
	documentation_url: Optional[str]
	case_study_url: Optional[str]  # External write-up / blog post

	# ── Highlights ───────────────────────────────────────────────────────────
	# Key measurable outcomes: [{"label": "Active users", "value": "10 k+"}]
	metrics: list[dict[str, Any]]
	# Main features: [{"title": "...", "description": "...", "icon_url": "..."}]
	features: list[dict[str, Any]]
	# Challenges & solutions: [{"challenge": "...", "solution": "..."}]
	challenges: list[dict[str, Any]]

	# ── Media ────────────────────────────────────────────────────────────────
	images: list[str]              # Screenshots, diagrams, demo GIFs
	featured: bool                 # Pin to homepage / hero section

	# ── Display ──────────────────────────────────────────────────────────────
	visible: bool
	order: int

	# ── Meta / i18n ──────────────────────────────────────────────────────────
	metadata: ContentMetadata
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None
	translations: dict = field(default_factory=dict)

	@property
	def is_deleted(self) -> bool:
		return self.deleted_at is not None

	@property
	def is_published(self) -> bool:
		return self.visible and not self.is_deleted
