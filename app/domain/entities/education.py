"""
Education entity for portfolio education history domain.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class Education:
	"""
	Education entity representing formal education history.

	First-class fields cover every piece of information relevant to a portfolio
	education entry. The ``metadata`` field is reserved for arbitrary extras
	that do not fit the structured schema.

	Degree types: bachelor, master, phd, associate, bootcamp, certification,
	              online_course, high_school, other.
	"""
	# ── Identity ─────────────────────────────────────────────────────────────
	id: int
	title: str                    # Full degree/programme title
	slug: str
	description: Optional[str]    # Short public-facing summary
	content: Optional[str]        # Long-form text: thesis, notes, etc. (Markdown)

	# ── Institution ──────────────────────────────────────────────────────────
	institution: str              # University / school name
	institution_url: Optional[str]  # Official institution website
	location: Optional[str]       # City, Country

	# ── Programme ────────────────────────────────────────────────────────────
	degree_type: str              # bachelor | master | phd | bootcamp | …
	field_of_study: Optional[str] # Computer Science, Design, etc.
	start_date: Optional[date]    # Programme start (YYYY-MM-DD)
	end_date: Optional[date]      # Graduation / expected end; None = ongoing

	# ── Credential ───────────────────────────────────────────────────────────
	credential_id: Optional[str]  # Official accreditation / diploma number
	credential_url: Optional[str] # Link to verifiable online credential
	grade: Optional[str]          # GPA, percentage, classification, etc.
	honors: Optional[str]         # Cum laude, distinction, valedictorian, etc.

	# ── Academic extras ──────────────────────────────────────────────────────
	# List of relevant subjects: ["Algorithms", "Distributed Systems", …]
	relevant_coursework: list[str]
	# Extracurricular activities: [{"name": "...", "role": "..."}]
	activities: list[dict[str, Any]]
	# Achievements / awards: [{"title": "...", "year": 2022, "description": "..."}]
	achievements: list[dict[str, Any]]

	# ── Media ────────────────────────────────────────────────────────────────
	images: list[str]             # Diploma scans, campus photos, etc.

	# ── Display ──────────────────────────────────────────────────────────────
	visible: bool
	order: int

	# ── Meta / i18n ──────────────────────────────────────────────────────────
	metadata: ContentMetadata     # Arbitrary extra key-value pairs
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None
	translations: dict = field(default_factory=dict)

	@property
	def is_ongoing(self) -> bool:
		"""True when the programme has no graduation date yet."""
		return self.end_date is None

	@property
	def is_deleted(self) -> bool:
		return self.deleted_at is not None

	@property
	def is_published(self) -> bool:
		return self.visible and not self.is_deleted
