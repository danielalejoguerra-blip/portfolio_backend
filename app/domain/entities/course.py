"""
Course entity for portfolio courses/certifications domain.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class Course:
	"""
	Course entity representing completed courses or certifications.
	
	Metadata can include:
	- platform: "Udemy", "Coursera", "Platzi", etc.
	- instructor: course instructor name
	- certificate_url: link to certificate
	- completion_date: when the course was completed
	- duration_hours: course duration
	- skills: list of skills learned
	- category: "backend", "frontend", "devops", etc.
	"""
	id: int
	title: str
	slug: str
	description: Optional[str]
	content: Optional[str]  # Detailed notes or review
	images: list[str]  # Certificate images, course thumbnails
	metadata: ContentMetadata
	visible: bool
	order: int
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
