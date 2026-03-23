"""
Personal information service containing business logic.
"""
from typing import Optional

from app.domain.entities.personal_info import PersonalInfo
from app.domain.repositories.personal_info_repository import PersonalInfoRepository
from app.services.ai_translation_service import AITranslationService


class PersonalInfoService:
	def __init__(self, repository: PersonalInfoRepository, ai_translation_service: AITranslationService = None) -> None:
		self.repository = repository
		self.ai_translation_service = ai_translation_service

	@staticmethod
	def _normalize_url(value: Optional[object]) -> Optional[str]:
		if value is None:
			return None
		return str(value)

	def create_personal_info(
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
		translations: dict = None,
	) -> PersonalInfo:
		# Auto-translate if no manual translations provided
		if not translations and self.ai_translation_service:
			translations = self.ai_translation_service.translate_fields(
				domain="personal_info",
				fields={"headline": headline, "bio": bio},
			)

		return self.repository.create(
			full_name=full_name,
			headline=headline,
			bio=bio,
			email=email,
			phone=phone,
			location=location,
			website=self._normalize_url(website),
			avatar_url=self._normalize_url(avatar_url),
			resume_url=self._normalize_url(resume_url),
			social_links=social_links,
			metadata=metadata,
			visible=visible,
			order=order,
			translations=translations,
		)

	def update_personal_info(
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
		translations: dict = None,
	) -> Optional[PersonalInfo]:
		# Auto-translate if no manual translations provided
		if translations is None and self.ai_translation_service:
			existing = self.repository.get_by_id(info_id)
			if existing:
				translations = self.ai_translation_service.translate_fields(
					domain="personal_info",
					fields={
						"headline": headline if headline is not None else existing.headline,
						"bio": bio if bio is not None else existing.bio,
					},
					existing_translations=existing.translations,
				)

		return self.repository.update(
			info_id=info_id,
			full_name=full_name,
			headline=headline,
			bio=bio,
			email=email,
			phone=phone,
			location=location,
			website=self._normalize_url(website),
			avatar_url=self._normalize_url(avatar_url),
			resume_url=self._normalize_url(resume_url),
			social_links=social_links,
			metadata=metadata,
			visible=visible,
			order=order,
			translations=translations,
		)

	def delete_personal_info(self, info_id: int, soft: bool = True) -> bool:
		return self.repository.delete(info_id, soft)

	def restore_personal_info(self, info_id: int) -> Optional[PersonalInfo]:
		return self.repository.restore(info_id)

	def get_personal_info_by_id(self, info_id: int) -> Optional[PersonalInfo]:
		return self.repository.get_by_id(info_id)

	def list_personal_info(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[PersonalInfo], int]:
		items = self.repository.list_all(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
			limit=limit,
			offset=offset,
		)
		total = self.repository.count(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
		)
		return items, total

	def get_public_personal_info(self, info_id: int) -> Optional[PersonalInfo]:
		info = self.repository.get_by_id(info_id)
		if info and info.is_published:
			return info
		return None

	def list_public_personal_info(
		self,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[PersonalInfo], int]:
		return self.list_personal_info(
			include_hidden=False,
			include_deleted=False,
			limit=limit,
			offset=offset,
		)
