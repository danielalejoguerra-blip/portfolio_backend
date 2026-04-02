"""
Course repository implementation with SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.content_base import ContentMetadata
from app.domain.entities.course import Course
from app.domain.repositories.course_repository import CourseRepository
from app.infrastructure.database.models.course_model import CourseModel


class CourseRepositoryImpl(CourseRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def _to_entity(self, model: CourseModel) -> Course:
		"""Map ORM model to domain entity"""
		return Course(
			id=model.id,
			title=model.title,
			slug=model.slug,
			description=model.description,
			content=model.content,
			is_certification=model.is_certification or False,
			category=model.category,
			level=model.level,
			platform=model.platform,
			platform_url=model.platform_url,
			instructor=model.instructor,
			instructor_url=model.instructor_url,
			completion_date=model.completion_date,
			expiration_date=model.expiration_date,
			duration_hours=model.duration_hours,
			credential_id=model.credential_id,
			certificate_url=model.certificate_url,
			certificate_image_url=model.certificate_image_url,
			badge_url=model.badge_url,
			skills_gained=model.skills_gained or [],
			syllabus=model.syllabus or [],
			images=model.images or [],
			visible=model.visible,
			order=model.order,
			metadata=ContentMetadata(data=model.meta or {}),
			created_at=model.created_at,
			updated_at=model.updated_at,
			deleted_at=model.deleted_at,
			translations=model.translations or {},
		)

	def get_by_id(self, course_id: int) -> Optional[Course]:
		model = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
		if not model:
			return None
		return self._to_entity(model)

	def get_by_slug(self, slug: str) -> Optional[Course]:
		model = self.db.query(CourseModel).filter(CourseModel.slug == slug).first()
		if not model:
			return None
		return self._to_entity(model)

	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[Course]:
		query = self.db.query(CourseModel)

		if not include_deleted:
			query = query.filter(CourseModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(CourseModel.visible == True)

		query = query.order_by(CourseModel.order.asc(), CourseModel.created_at.desc())

		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		return [self._to_entity(m) for m in query.all()]

	def count(self, include_hidden: bool = False, include_deleted: bool = False) -> int:
		query = self.db.query(CourseModel)

		if not include_deleted:
			query = query.filter(CourseModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(CourseModel.visible == True)

		return query.count()

	def create(
		self,
		title: str,
		slug: str,
		description: Optional[str] = None,
		content: Optional[str] = None,
		is_certification: bool = False,
		category: Optional[str] = None,
		level: Optional[str] = None,
		platform: Optional[str] = None,
		platform_url: Optional[str] = None,
		instructor: Optional[str] = None,
		instructor_url: Optional[str] = None,
		completion_date=None,
		expiration_date=None,
		duration_hours: Optional[int] = None,
		credential_id: Optional[str] = None,
		certificate_url: Optional[str] = None,
		certificate_image_url: Optional[str] = None,
		badge_url: Optional[str] = None,
		skills_gained: Optional[list] = None,
		syllabus: Optional[list] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
		translations: dict = None,
	) -> Course:
		model = CourseModel(
			title=title, slug=slug, description=description, content=content,
			is_certification=is_certification, category=category, level=level,
			platform=platform, platform_url=platform_url,
			instructor=instructor, instructor_url=instructor_url,
			completion_date=completion_date, expiration_date=expiration_date,
			duration_hours=duration_hours, credential_id=credential_id,
			certificate_url=certificate_url, certificate_image_url=certificate_image_url,
			badge_url=badge_url, skills_gained=skills_gained or [],
			syllabus=syllabus or [], images=images or [],
			meta=metadata or {}, visible=visible, order=order,
			translations=translations or {},
		)
		self.db.add(model)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def update(
		self,
		course_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		is_certification: Optional[bool] = None,
		category: Optional[str] = None,
		level: Optional[str] = None,
		platform: Optional[str] = None,
		platform_url: Optional[str] = None,
		instructor: Optional[str] = None,
		instructor_url: Optional[str] = None,
		completion_date=None,
		expiration_date=None,
		duration_hours: Optional[int] = None,
		credential_id: Optional[str] = None,
		certificate_url: Optional[str] = None,
		certificate_image_url: Optional[str] = None,
		badge_url: Optional[str] = None,
		skills_gained: Optional[list] = None,
		syllabus: Optional[list] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
		translations: dict = None,
	) -> Optional[Course]:
		model = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
		if not model:
			return None

		for attr, val in [
			("title", title), ("slug", slug), ("description", description), ("content", content),
			("is_certification", is_certification), ("category", category), ("level", level),
			("platform", platform), ("platform_url", platform_url),
			("instructor", instructor), ("instructor_url", instructor_url),
			("completion_date", completion_date), ("expiration_date", expiration_date),
			("duration_hours", duration_hours), ("credential_id", credential_id),
			("certificate_url", certificate_url), ("certificate_image_url", certificate_image_url),
			("badge_url", badge_url), ("skills_gained", skills_gained),
			("syllabus", syllabus), ("images", images),
			("visible", visible), ("order", order), ("translations", translations),
		]:
			if val is not None:
				setattr(model, attr, val)
		if metadata is not None:
			model.meta = metadata

		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def delete(self, course_id: int, soft: bool = True) -> bool:
		model = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
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

	def restore(self, course_id: int) -> Optional[Course]:
		model = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
		if not model:
			return None

		model.deleted_at = None
		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		query = self.db.query(CourseModel).filter(CourseModel.slug == slug)
		if exclude_id:
			query = query.filter(CourseModel.id != exclude_id)
		return query.first() is not None
