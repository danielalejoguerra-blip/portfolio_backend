"""
Blog repository implementation with SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.blog import BlogPost
from app.domain.entities.content_base import ContentMetadata
from app.domain.repositories.blog_repository import BlogRepository
from app.infrastructure.database.models.blog_model import BlogPostModel


class BlogRepositoryImpl(BlogRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def _to_entity(self, model: BlogPostModel) -> BlogPost:
		"""Map ORM model to domain entity"""
		return BlogPost(
			id=model.id,
			title=model.title,
			slug=model.slug,
			description=model.description,
			content=model.content,
			images=model.images or [],
			metadata=ContentMetadata(data=model.meta or {}),
			visible=model.visible,
			published_at=model.published_at,
			created_at=model.created_at,
			updated_at=model.updated_at,
			deleted_at=model.deleted_at,
			translations=model.translations or {},
		)

	def get_by_id(self, post_id: int) -> Optional[BlogPost]:
		model = self.db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
		if not model:
			return None
		return self._to_entity(model)

	def get_by_slug(self, slug: str) -> Optional[BlogPost]:
		model = self.db.query(BlogPostModel).filter(BlogPostModel.slug == slug).first()
		if not model:
			return None
		return self._to_entity(model)

	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		include_scheduled: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[BlogPost]:
		query = self.db.query(BlogPostModel)

		if not include_deleted:
			query = query.filter(BlogPostModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(BlogPostModel.visible == True)
		if not include_scheduled:
			# Only show posts that are either published (published_at is null or in the past)
			now = datetime.now(timezone.utc)
			query = query.filter(
				(BlogPostModel.published_at.is_(None)) | (BlogPostModel.published_at <= now)
			)

		query = query.order_by(BlogPostModel.published_at.desc().nullsfirst(), BlogPostModel.created_at.desc())

		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		return [self._to_entity(m) for m in query.all()]

	def count(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		include_scheduled: bool = False,
	) -> int:
		query = self.db.query(BlogPostModel)

		if not include_deleted:
			query = query.filter(BlogPostModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(BlogPostModel.visible == True)
		if not include_scheduled:
			now = datetime.now(timezone.utc)
			query = query.filter(
				(BlogPostModel.published_at.is_(None)) | (BlogPostModel.published_at <= now)
			)

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
		published_at: Optional[datetime] = None,
		translations: dict = None,
	) -> BlogPost:
		model = BlogPostModel(
			title=title,
			slug=slug,
			description=description,
			content=content,
			images=images or [],
			meta=metadata or {},
			visible=visible,
			published_at=published_at,
			translations=translations or {},
		)
		self.db.add(model)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

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
		translations: dict = None,
	) -> Optional[BlogPost]:
		model = self.db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
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
		if published_at is not None:
			model.published_at = published_at
		if translations is not None:
			model.translations = translations

		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def delete(self, post_id: int, soft: bool = True) -> bool:
		model = self.db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
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

	def restore(self, post_id: int) -> Optional[BlogPost]:
		model = self.db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
		if not model:
			return None

		model.deleted_at = None
		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		query = self.db.query(BlogPostModel).filter(BlogPostModel.slug == slug)
		if exclude_id:
			query = query.filter(BlogPostModel.id != exclude_id)
		return query.first() is not None
