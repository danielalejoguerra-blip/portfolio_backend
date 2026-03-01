"""
Skill entity for portfolio skills domain.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class Skill:
	"""
	Skill entity representing a skill entry for portfolio.

	Metadata can include:
	- level: "beginner", "intermediate", "advanced", "expert"
	- category: "backend", "frontend", "devops", etc.
	- years_experience: years using the skill
	- icon: icon identifier for UI
	"""
	id: int
	title: str
	slug: str
	description: Optional[str]
	metadata: ContentMetadata
	visible: bool
	order: int
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None

	@property
	def is_deleted(self) -> bool:
		return self.deleted_at is not None

	@property
	def is_published(self) -> bool:
		return self.visible and not self.is_deleted
