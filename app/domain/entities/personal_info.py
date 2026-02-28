"""
PersonalInfo entity for portfolio personal information domain.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class PersonalInfo:
	"""
	Personal information entity for portfolio profile/about/contact.

	Metadata can include:
	- keywords: ["backend", "fastapi", "postgres"]
	- availability: "open_to_work"
	- extra_links: {"github": "...", "linkedin": "..."}
	"""
	id: int
	full_name: str
	headline: Optional[str]
	bio: Optional[str]
	email: Optional[str]
	phone: Optional[str]
	location: Optional[str]
	website: Optional[str]
	avatar_url: Optional[str]
	resume_url: Optional[str]
	social_links: dict[str, str]
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
