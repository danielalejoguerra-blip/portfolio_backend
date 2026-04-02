"""
Course entity for portfolio courses/certifications domain.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class Course:
	"""
	Course entity representing completed courses or certifications.

	Distinguishes between a learning *course* (``is_certification=False``) and
	an official *certification* (``is_certification=True``) that may carry a
	credential ID and expiration date.

	Level values: beginner | intermediate | advanced | expert.
	Category values: backend | frontend | mobile | devops | data | design |
	                 security | cloud | soft_skills | other.
	"""
	# ── Identity ─────────────────────────────────────────────────────────────
	id: int
	title: str
	slug: str
	description: Optional[str]         # Short public-facing summary
	content: Optional[str]             # Personal notes / review (Markdown)

	# ── Classification ───────────────────────────────────────────────────────
	is_certification: bool             # True = official cert; False = course
	category: Optional[str]            # backend | frontend | devops | …
	level: Optional[str]               # beginner | intermediate | advanced | expert

	# ── Platform ─────────────────────────────────────────────────────────────
	platform: Optional[str]            # Udemy | Coursera | Platzi | AWS | Google
	platform_url: Optional[str]        # Course page on the platform
	instructor: Optional[str]          # Instructor / organisation name
	instructor_url: Optional[str]      # Instructor profile / organisation URL

	# ── Timeline ─────────────────────────────────────────────────────────────
	completion_date: Optional[date]    # Date the course / exam was completed
	expiration_date: Optional[date]    # Cert expiry (None = does not expire)
	duration_hours: Optional[int]      # Approximate course length in hours

	# ── Credential ───────────────────────────────────────────────────────────
	credential_id: Optional[str]       # Official certificate / badge ID
	certificate_url: Optional[str]     # Shareable certificate verification URL
	certificate_image_url: Optional[str]  # Certificate image (PDF preview / PNG)
	badge_url: Optional[str]           # Digital badge (Credly, Acclaim, etc.)

	# ── Learning outcomes ────────────────────────────────────────────────────
	# Skills gained: [{"name": "Kubernetes", "category": "devops"}]
	skills_gained: list[dict[str, Any]]
	# Syllabus sections: [{"title": "...", "topics": ["...", "..."]}]
	syllabus: list[dict[str, Any]]

	# ── Media ────────────────────────────────────────────────────────────────
	images: list[str]                  # Certificate scans, thumbnails

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
	def is_expired(self) -> bool:
		"""True when a certification has passed its expiration date."""
		if self.expiration_date is None:
			return False
		return date.today() > self.expiration_date

	@property
	def is_deleted(self) -> bool:
		return self.deleted_at is not None

	@property
	def is_published(self) -> bool:
		return self.visible and not self.is_deleted
