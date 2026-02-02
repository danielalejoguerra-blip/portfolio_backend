"""
Education entity for portfolio education history domain.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class Education:
	"""
	Education entity representing formal education history.
	
	Metadata can include:
	- institution: university/school name
	- degree: "Bachelor's", "Master's", "PhD", etc.
	- field_of_study: "Computer Science", etc.
	- start_date: education start date
	- end_date: graduation date (null if ongoing)
	- gpa: grade point average
	- achievements: list of notable achievements
	- location: institution location
	"""
	id: int
	title: str  # Degree title
	slug: str
	description: Optional[str]
	content: Optional[str]  # Detailed description, thesis, etc.
	images: list[str]  # Diploma, campus photos
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
