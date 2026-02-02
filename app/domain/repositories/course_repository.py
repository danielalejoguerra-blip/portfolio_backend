"""
Course repository interface.
Defines contract for course data access operations.
"""
from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.course import Course


class CourseRepository(ABC):
	@abstractmethod
	def get_by_id(self, course_id: int) -> Optional[Course]:
		raise NotImplementedError()

	@abstractmethod
	def get_by_slug(self, slug: str) -> Optional[Course]:
		raise NotImplementedError()

	@abstractmethod
	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[Course]:
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
	) -> Course:
		raise NotImplementedError()

	@abstractmethod
	def update(
		self,
		course_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
	) -> Optional[Course]:
		raise NotImplementedError()

	@abstractmethod
	def delete(self, course_id: int, soft: bool = True) -> bool:
		raise NotImplementedError()

	@abstractmethod
	def restore(self, course_id: int) -> Optional[Course]:
		raise NotImplementedError()

	@abstractmethod
	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		raise NotImplementedError()
