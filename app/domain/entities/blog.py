"""
Blog post entity for portfolio blog domain.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class BlogPost:
	"""
	Blog post entity for articles and publications.
	
	Metadata can include:
	- tags: list of topic tags
	- category: "tutorial", "opinion", "case_study", etc.
	- reading_time: estimated minutes to read
	- featured: bool for homepage highlight
	- canonical_url: original publication URL if cross-posted
	"""
	id: int
	title: str
	slug: str
	description: Optional[str]  # Excerpt/summary
	content: Optional[str]  # Full article in Markdown/HTML
	images: list[str]
	metadata: ContentMetadata
	visible: bool
	published_at: Optional[datetime]  # Scheduled publishing
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None

	@property
	def is_deleted(self) -> bool:
		return self.deleted_at is not None

	@property
	def is_published(self) -> bool:
		if self.is_deleted or not self.visible:
			return False
		if self.published_at is None:
			return True
		return self.published_at <= datetime.now(self.published_at.tzinfo)
