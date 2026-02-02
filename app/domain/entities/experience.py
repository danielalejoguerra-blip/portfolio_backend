"""
Experience entity for portfolio work experience domain.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class Experience:
	"""
	Experience entity representing work/professional experience.
	
	Metadata can include:
	- company: employer name
	- position: job title
	- location: office location
	- start_date: employment start date
	- end_date: employment end date (null if current)
	- is_current: bool indicating current employment
	- employment_type: "full_time", "part_time", "contract", "freelance"
	- tech_stack: technologies used
	- achievements: list of key accomplishments
	- company_logo: URL to company logo
	"""
	id: int
	title: str  # Position/role title
	slug: str
	description: Optional[str]  # Brief role description
	content: Optional[str]  # Detailed responsibilities and achievements
	images: list[str]
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
