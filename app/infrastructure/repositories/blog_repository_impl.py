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
			content_blocks=model.content_blocks or [],
			cover_image_url=model.cover_image_url,
			cover_image_alt=model.cover_image_alt,
			cover_image_position=model.cover_image_position or "center",
			category=model.category,
			tags=model.tags or [],
			series=model.series,
			series_order=model.series_order,
			reading_time_minutes=model.reading_time_minutes,
			featured=model.featured or False,
			seo_title=model.seo_title,
			seo_description=model.seo_description,
			canonical_url=model.canonical_url,
			og_image_url=model.og_image_url,
			images=model.images or [],
			visible=model.visible,
			published_at=model.published_at,
			metadata=ContentMetadata(data=model.meta or {}),
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
		content_blocks: Optional[list] = None,
		cover_image_url: Optional[str] = None,
		cover_image_alt: Optional[str] = None,
		cover_image_position: str = "center",
		category: Optional[str] = None,
		tags: Optional[list] = None,
		series: Optional[str] = None,
		series_order: Optional[int] = None,
		reading_time_minutes: Optional[int] = None,
		featured: bool = False,
		seo_title: Optional[str] = None,
		seo_description: Optional[str] = None,
		canonical_url: Optional[str] = None,
		og_image_url: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		published_at: Optional[datetime] = None,
		translations: dict = None,
	) -> BlogPost:
		model = BlogPostModel(
			title=title, slug=slug, description=description, content=content,
			content_blocks=content_blocks or [],
			cover_image_url=cover_image_url, cover_image_alt=cover_image_alt,
			cover_image_position=cover_image_position,
			category=category, tags=tags or [],
			series=series, series_order=series_order,
			reading_time_minutes=reading_time_minutes, featured=featured,
			seo_title=seo_title, seo_description=seo_description,
			canonical_url=canonical_url, og_image_url=og_image_url,
			images=images or [], meta=metadata or {},
			visible=visible, published_at=published_at,
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
		content_blocks: Optional[list] = None,
		cover_image_url: Optional[str] = None,
		cover_image_alt: Optional[str] = None,
		cover_image_position: Optional[str] = None,
		category: Optional[str] = None,
		tags: Optional[list] = None,
		series: Optional[str] = None,
		series_order: Optional[int] = None,
		reading_time_minutes: Optional[int] = None,
		featured: Optional[bool] = None,
		seo_title: Optional[str] = None,
		seo_description: Optional[str] = None,
		canonical_url: Optional[str] = None,
		og_image_url: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		published_at: Optional[datetime] = None,
		translations: dict = None,
	) -> Optional[BlogPost]:
		model = self.db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
		if not model:
			return None

		for attr, val in [
			("title", title), ("slug", slug), ("description", description), ("content", content),
			("content_blocks", content_blocks), ("cover_image_url", cover_image_url),
			("cover_image_alt", cover_image_alt), ("cover_image_position", cover_image_position),
			("category", category), ("tags", tags), ("series", series),
			("series_order", series_order), ("reading_time_minutes", reading_time_minutes),
			("featured", featured), ("seo_title", seo_title),
			("seo_description", seo_description), ("canonical_url", canonical_url),
			("og_image_url", og_image_url), ("images", images),
			("visible", visible), ("published_at", published_at), ("translations", translations),
		]:
			if val is not None:
				setattr(model, attr, val)
		if metadata is not None:
			model.meta = metadata

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
