"""
Personal information repository implementation with SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.content_base import ContentMetadata
from app.domain.entities.personal_info import PersonalInfo
from app.domain.repositories.personal_info_repository import PersonalInfoRepository
from app.infrastructure.database.models.personal_info_model import PersonalInfoModel


class PersonalInfoRepositoryImpl(PersonalInfoRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def _to_entity(self, model: PersonalInfoModel) -> PersonalInfo:
		return PersonalInfo(
			id=model.id,
			full_name=model.full_name,
			headline=model.headline,
			bio=model.bio,
			email=model.email,
			phone=model.phone,
			location=model.location,
			website=model.website,
			avatar_url=model.avatar_url,
			resume_url=model.resume_url,
			social_links=model.social_links or {},
			metadata=ContentMetadata(data=model.meta or {}),
			visible=model.visible,
			order=model.order,
			created_at=model.created_at,
			updated_at=model.updated_at,
			deleted_at=model.deleted_at,
		)

	def get_by_id(self, info_id: int) -> Optional[PersonalInfo]:
		model = self.db.query(PersonalInfoModel).filter(PersonalInfoModel.id == info_id).first()
		if not model:
			return None
		return self._to_entity(model)

	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[PersonalInfo]:
		query = self.db.query(PersonalInfoModel)

		if not include_deleted:
			query = query.filter(PersonalInfoModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(PersonalInfoModel.visible == True)

		query = query.order_by(PersonalInfoModel.order.asc(), PersonalInfoModel.created_at.desc())

		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		return [self._to_entity(m) for m in query.all()]

	def count(self, include_hidden: bool = False, include_deleted: bool = False) -> int:
		query = self.db.query(PersonalInfoModel)

		if not include_deleted:
			query = query.filter(PersonalInfoModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(PersonalInfoModel.visible == True)

		return query.count()

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
		model = PersonalInfoModel(
			full_name=full_name,
			headline=headline,
			bio=bio,
			email=email,
			phone=phone,
			location=location,
			website=website,
			avatar_url=avatar_url,
			resume_url=resume_url,
			social_links=social_links or {},
			meta=metadata or {},
			visible=visible,
			order=order,
		)
		self.db.add(model)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

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
		model = self.db.query(PersonalInfoModel).filter(PersonalInfoModel.id == info_id).first()
		if not model:
			return None

		if full_name is not None:
			model.full_name = full_name
		if headline is not None:
			model.headline = headline
		if bio is not None:
			model.bio = bio
		if email is not None:
			model.email = email
		if phone is not None:
			model.phone = phone
		if location is not None:
			model.location = location
		if website is not None:
			model.website = website
		if avatar_url is not None:
			model.avatar_url = avatar_url
		if resume_url is not None:
			model.resume_url = resume_url
		if social_links is not None:
			model.social_links = social_links
		if metadata is not None:
			model.meta = metadata
		if visible is not None:
			model.visible = visible
		if order is not None:
			model.order = order

		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def delete(self, info_id: int, soft: bool = True) -> bool:
		model = self.db.query(PersonalInfoModel).filter(PersonalInfoModel.id == info_id).first()
		if not model:
			return False

		if soft:
			model.deleted_at = datetime.now(timezone.utc)
			model.updated_at = datetime.now(timezone.utc)
			self.db.commit()
		else:
			self.db.delete(model)
			self.db.commit()

		return True

	def restore(self, info_id: int) -> Optional[PersonalInfo]:
		model = self.db.query(PersonalInfoModel).filter(PersonalInfoModel.id == info_id).first()
		if not model:
			return None

		model.deleted_at = None
		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)
