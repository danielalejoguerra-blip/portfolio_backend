"""
Project repository implementation with SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.content_base import ContentMetadata
from app.domain.entities.project import Project
from app.domain.repositories.project_repository import ProjectRepository
from app.infrastructure.database.models.project_model import ProjectModel


class ProjectRepositoryImpl(ProjectRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def _to_entity(self, model: ProjectModel) -> Project:
		"""Map ORM model to domain entity"""
		return Project(
			id=model.id,
			title=model.title,
			slug=model.slug,
			description=model.description,
			content=model.content,
			images=model.images or [],
			metadata=ContentMetadata(data=model.meta or {}),
			visible=model.visible,
			order=model.order,
			created_at=model.created_at,
			updated_at=model.updated_at,
			deleted_at=model.deleted_at,
			translations=model.translations or {},
		)

	def get_by_id(self, project_id: int) -> Optional[Project]:
		model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
		if not model:
			return None
		return self._to_entity(model)

	def get_by_slug(self, slug: str) -> Optional[Project]:
		model = self.db.query(ProjectModel).filter(ProjectModel.slug == slug).first()
		if not model:
			return None
		return self._to_entity(model)

	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[Project]:
		query = self.db.query(ProjectModel)

		if not include_deleted:
			query = query.filter(ProjectModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(ProjectModel.visible == True)

		query = query.order_by(ProjectModel.order.asc(), ProjectModel.created_at.desc())

		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		return [self._to_entity(m) for m in query.all()]

	def count(self, include_hidden: bool = False, include_deleted: bool = False) -> int:
		query = self.db.query(ProjectModel)

		if not include_deleted:
			query = query.filter(ProjectModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(ProjectModel.visible == True)

		return query.count()

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
	) -> Project:
		model = ProjectModel(
			title=title,
			slug=slug,
			description=description,
			content=content,
			images=images or [],
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
		project_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
		translations: dict = None,
	) -> Optional[Project]:
		model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
		if not model:
			return None

		if title is not None:
			model.title = title
		if slug is not None:
			model.slug = slug
		if description is not None:
			model.description = description
		if content is not None:
			model.content = content
		if images is not None:
			model.images = images
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

	def delete(self, project_id: int, soft: bool = True) -> bool:
		model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
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

	def restore(self, project_id: int) -> Optional[Project]:
		model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
		if not model:
			return None

		model.deleted_at = None
		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		query = self.db.query(ProjectModel).filter(ProjectModel.slug == slug)
		if exclude_id:
			query = query.filter(ProjectModel.id != exclude_id)
		return query.first() is not None
