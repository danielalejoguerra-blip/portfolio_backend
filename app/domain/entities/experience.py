"""
Experience entity for portfolio work experience domain.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class Experience:
	"""
	Experience entity representing professional / work experience.

	First-class fields cover every detail a professional portfolio entry needs.
	The ``metadata`` field is reserved for arbitrary extras.

	Employment type values:
	  full_time | part_time | contract | freelance | internship | volunteer.
	Work mode values:
	  on_site | remote | hybrid.
	"""
	# ── Identity ─────────────────────────────────────────────────────────────
	id: int
	title: str                     # Job title / role
	slug: str
	description: Optional[str]     # Short public-facing summary
	content: Optional[str]         # Long-form responsibilities & achievements (Markdown)

	# ── Company ─────────────────────────────────────────────────────────────
	company: str                   # Employer / organisation name
	company_url: Optional[str]     # Official company website
	company_logo_url: Optional[str]  # Company logo image URL
	location: Optional[str]        # City, Country (or "Remote")

	# ── Role details ───────────────────────────────────────────────────────
	employment_type: str           # full_time | part_time | contract | freelance | …
	work_mode: Optional[str]       # on_site | remote | hybrid
	department: Optional[str]      # Engineering, Product, Design, etc.

	# ── Timeline ─────────────────────────────────────────────────────────────
	start_date: date
	end_date: Optional[date]       # None when is_current = True
	# is_current is derived; stored as a shorthand bool for the ORM layer
	is_current: bool

	# ── Tech stack ───────────────────────────────────────────────────────────
	# [{"name": "FastAPI", "category": "backend", "icon_url": "..."}]
	tech_stack: list[dict[str, Any]]

	# ── Highlights ───────────────────────────────────────────────────────────
	# Key responsibilities: ["Designed REST API", "Led migrations", ...]
	responsibilities: list[str]
	# Measurable achievements: [{"label": "Uptime", "value": "99.9%"}]
	achievements: list[dict[str, Any]]
	# Related projects during this role: [{"title": "...", "slug": "...", "url": "..."}]
	related_projects: list[dict[str, Any]]

	# ── References ───────────────────────────────────────────────────────────
	# [{"name": "...", "role": "...", "linkedin_url": "...", "available": true}]
	references: list[dict[str, Any]]

	# ── Media ────────────────────────────────────────────────────────────────
	images: list[str]              # Office photos, team pictures, etc.

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

