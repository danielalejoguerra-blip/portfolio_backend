"""
Education repository interface.
Defines contract for education data access operations.
"""
from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.education import Education


class EducationRepository(ABC):
	@abstractmethod
	def get_by_id(self, education_id: int) -> Optional[Education]:
		raise NotImplementedError()

	@abstractmethod
	def get_by_slug(self, slug: str) -> Optional[Education]:
		raise NotImplementedError()

	@abstractmethod
	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[Education]:
		raise NotImplementedError()

	@abstractmethod
	def count(self, include_hidden: bool = False, include_deleted: bool = False) -> int:
		raise NotImplementedError()

	@abstractmethod
	def create(
		self,
		title: str,
		slug: str,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
		translations: dict = None,
	) -> Education:
		raise NotImplementedError()

	@abstractmethod
	def update(
		self,
		education_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
		translations: dict = None,
	) -> Optional[Education]:
		raise NotImplementedError()

	@abstractmethod
	def delete(self, education_id: int, soft: bool = True) -> bool:
		raise NotImplementedError()

	@abstractmethod
	def restore(self, education_id: int) -> Optional[Education]:
		raise NotImplementedError()

	@abstractmethod
	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		raise NotImplementedError()
