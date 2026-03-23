"""
Project entity for portfolio projects domain.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class Project:
	"""
	Project entity representing a portfolio project.
	
	Metadata can include:
	- tech_stack: list of technologies used
	- links: {"github": "...", "demo": "...", "docs": "..."}
	- featured: bool for homepage highlight
	- category: "web", "mobile", "api", etc.
	- status: "completed", "in_progress", "archived"
	"""
	id: int
	title: str
	slug: str
	description: Optional[str]
	content: Optional[str]
	images: list[str]
	metadata: ContentMetadata
	visible: bool
	order: int  # Display order
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
