"""
Personal information repository interface.
Defines contract for personal info data access operations.
"""
from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.personal_info import PersonalInfo


class PersonalInfoRepository(ABC):
	@abstractmethod
	def get_by_id(self, info_id: int) -> Optional[PersonalInfo]:
		raise NotImplementedError()

	@abstractmethod
	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[PersonalInfo]:
		raise NotImplementedError()

	@abstractmethod
	def count(self, include_hidden: bool = False, include_deleted: bool = False) -> int:
		raise NotImplementedError()

	@abstractmethod
	def create(
		self,
		full_name: str,
		headline: Optional[str] = None,
		bio: Optional[str] = None,
		email: Optional[str] = None,
		phone: Optional[str] = None,
		location: Optional[str] = None,
		website: Optional[str] = None,
		avatar_url: Optional[str] = None,
		resume_url: Optional[str] = None,
		social_links: Optional[dict[str, str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
	) -> PersonalInfo:
		raise NotImplementedError()

	@abstractmethod
	def update(
		self,
		info_id: int,
		full_name: Optional[str] = None,
		headline: Optional[str] = None,
		bio: Optional[str] = None,
		email: Optional[str] = None,
		phone: Optional[str] = None,
		location: Optional[str] = None,
		website: Optional[str] = None,
		avatar_url: Optional[str] = None,
		resume_url: Optional[str] = None,
		social_links: Optional[dict[str, str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
	) -> Optional[PersonalInfo]:
		raise NotImplementedError()

	@abstractmethod
	def delete(self, info_id: int, soft: bool = True) -> bool:
		raise NotImplementedError()

	@abstractmethod
	def restore(self, info_id: int) -> Optional[PersonalInfo]:
		raise NotImplementedError()
