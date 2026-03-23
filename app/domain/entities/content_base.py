"""
Base content entity and value objects for all content domains.
Provides shared structure for Projects, Blog, Courses, Education, Experience.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass(frozen=True)
class ContentMetadata:
	"""
	Value Object for flexible metadata storage.
	Allows storing arbitrary key-value pairs without schema migrations.
	
	Common use cases:
	- tech_stack: ["Python", "FastAPI", "PostgreSQL"]
	- links: {"github": "...", "demo": "..."}
	- dates: {"start": "2024-01", "end": "2024-06"}
	- icons: {"main": "project-icon.svg"}
	"""
	data: dict[str, Any] = field(default_factory=dict)

	def get(self, key: str, default: Any = None) -> Any:
		return self.data.get(key, default)

	def to_dict(self) -> dict[str, Any]:
		return self.data.copy()


@dataclass(frozen=True)
class ContentBase:
	"""
	Base content entity with common fields for all content types.
	Immutable to ensure domain integrity.
	"""
	id: int
	title: str
	slug: str
	description: Optional[str]
	content: Optional[str]  # Markdown/HTML content
	images: list[str]  # List of image URLs
	metadata: ContentMetadata
	visible: bool
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None  # Soft delete support
	translations: dict = field(default_factory=dict)

	@property
	def is_deleted(self) -> bool:
		return self.deleted_at is not None

	@property
	def is_published(self) -> bool:
		"""Content is published if visible and not deleted"""
		return self.visible and not self.is_deleted
