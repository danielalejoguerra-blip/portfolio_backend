"""
Skill repository implementation with SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.content_base import ContentMetadata
from app.domain.entities.skill import Skill
from app.domain.repositories.skill_repository import SkillRepository
from app.infrastructure.database.models.skill_model import SkillModel


class SkillRepositoryImpl(SkillRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def _to_entity(self, model: SkillModel) -> Skill:
		"""Map ORM model to domain entity"""
		return Skill(
			id=model.id,
			title=model.title,
			slug=model.slug,
			description=model.description,
			metadata=ContentMetadata(data=model.meta or {}),
			visible=model.visible,
			order=model.order,
			created_at=model.created_at,
			updated_at=model.updated_at,
			deleted_at=model.deleted_at,
			translations=model.translations or {},
		)

	def get_by_id(self, skill_id: int) -> Optional[Skill]:
		model = self.db.query(SkillModel).filter(SkillModel.id == skill_id).first()
		if not model:
			return None
		return self._to_entity(model)

	def get_by_slug(self, slug: str) -> Optional[Skill]:
		model = self.db.query(SkillModel).filter(SkillModel.slug == slug).first()
		if not model:
			return None
		return self._to_entity(model)

	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[Skill]:
		query = self.db.query(SkillModel)

		if not include_deleted:
			query = query.filter(SkillModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(SkillModel.visible.is_(True))

		query = query.order_by(SkillModel.order.asc(), SkillModel.created_at.desc())

		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		return [self._to_entity(m) for m in query.all()]

	def count(self, include_hidden: bool = False, include_deleted: bool = False) -> int:
		query = self.db.query(SkillModel)

		if not include_deleted:
			query = query.filter(SkillModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(SkillModel.visible.is_(True))

		return query.count()

	def create(
		self,
		title: str,
		slug: str,
		description: Optional[str] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
		translations: dict = None,
	) -> Skill:
		model = SkillModel(
			title=title,
			slug=slug,
			description=description,
			meta=metadata or {},
			visible=visible,
			order=order,
			translations=translations or {},
		)
		self.db.add(model)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def update(
		self,
		skill_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
		translations: dict = None,
	) -> Optional[Skill]:
		model = self.db.query(SkillModel).filter(SkillModel.id == skill_id).first()
		if not model:
			return None

		if title is not None:
			model.title = title
		if slug is not None:
			model.slug = slug
		if description is not None:
			model.description = description
		if metadata is not None:
			model.meta = metadata
		if visible is not None:
			model.visible = visible
		if order is not None:
			model.order = order
		if translations is not None:
			model.translations = translations

		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def delete(self, skill_id: int, soft: bool = True) -> bool:
		model = self.db.query(SkillModel).filter(SkillModel.id == skill_id).first()
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

	def restore(self, skill_id: int) -> Optional[Skill]:
		model = self.db.query(SkillModel).filter(SkillModel.id == skill_id).first()
		if not model:
			return None

		model.deleted_at = None
		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		query = self.db.query(SkillModel).filter(SkillModel.slug == slug)
		if exclude_id:
			query = query.filter(SkillModel.id != exclude_id)
		return query.first() is not None
