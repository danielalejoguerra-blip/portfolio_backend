"""
Blog repository interface.
Defines contract for blog post data access operations.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.domain.entities.blog import BlogPost


class BlogRepository(ABC):
	@abstractmethod
	def get_by_id(self, post_id: int) -> Optional[BlogPost]:
		raise NotImplementedError()

	@abstractmethod
	def get_by_slug(self, slug: str) -> Optional[BlogPost]:
		raise NotImplementedError()

	@abstractmethod
	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		include_scheduled: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[BlogPost]:
		raise NotImplementedError()

	@abstractmethod
	def count(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		include_scheduled: bool = False,
	) -> int:
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
		published_at: Optional[datetime] = None,
	) -> BlogPost:
		raise NotImplementedError()

	@abstractmethod
	def update(
		self,
		post_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		published_at: Optional[datetime] = None,
	) -> Optional[BlogPost]:
		raise NotImplementedError()

	@abstractmethod
	def delete(self, post_id: int, soft: bool = True) -> bool:
		raise NotImplementedError()

	@abstractmethod
	def restore(self, post_id: int) -> Optional[BlogPost]:
		raise NotImplementedError()

	@abstractmethod
	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		raise NotImplementedError()
