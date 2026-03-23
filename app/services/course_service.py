"""
Course service containing business logic for courses domain.
"""
import re
import unicodedata
from typing import Optional

from app.domain.entities.course import Course
from app.domain.repositories.course_repository import CourseRepository
from app.services.ai_translation_service import AITranslationService


class CourseService:
	def __init__(self, repository: CourseRepository, ai_translation_service: AITranslationService = None) -> None:
		self.repository = repository
		self.ai_translation_service = ai_translation_service

	def _generate_slug(self, title: str) -> str:
		"""Generate URL-friendly slug from title"""
		slug = unicodedata.normalize("NFKD", title.lower())
		slug = slug.encode("ascii", "ignore").decode("ascii")
		slug = re.sub(r"[^a-z0-9]+", "-", slug)
		slug = slug.strip("-")
		slug = re.sub(r"-+", "-", slug)
		return slug

	def _ensure_unique_slug(self, slug: str, exclude_id: Optional[int] = None) -> str:
		"""Ensure slug is unique by appending number if necessary"""
		original_slug = slug
		counter = 1
		while self.repository.slug_exists(slug, exclude_id):
			slug = f"{original_slug}-{counter}"
			counter += 1
		return slug

	def create_course(
		self,
		title: str,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
		translations: dict = None,
	) -> Course:
		if not slug:
			slug = self._generate_slug(title)

		slug = self._ensure_unique_slug(slug)

		# Auto-translate if no manual translations provided
		if not translations and self.ai_translation_service:
			translations = self.ai_translation_service.translate_fields(
				domain="course",
				fields={"description": description, "content": content},
			)

		return self.repository.create(
			title=title,
			slug=slug,
			description=description,
			content=content,
			images=images,
			metadata=metadata,
			visible=visible,
			order=order,
			translations=translations,
		)

	def update_course(
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
		translations: dict = None,
	) -> Optional[Course]:
		existing = self.repository.get_by_id(course_id)
		if not existing:
			return None

		if slug and slug != existing.slug:
			if self.repository.slug_exists(slug, course_id):
				raise ValueError("slug_already_exists")

		# Auto-translate if no manual translations provided
		if translations is None and self.ai_translation_service:
			translate_fields = {
				"description": description if description is not None else existing.description,
				"content": content if content is not None else existing.content,
			}
			translations = self.ai_translation_service.translate_fields(
				domain="course",
				fields=translate_fields,
				existing_translations=existing.translations,
			)

		return self.repository.update(
			course_id=course_id,
			title=title,
			slug=slug,
			description=description,
			content=content,
			images=images,
			metadata=metadata,
			visible=visible,
			order=order,
			translations=translations,
		)

	def delete_course(self, course_id: int, soft: bool = True) -> bool:
		return self.repository.delete(course_id, soft)

	def restore_course(self, course_id: int) -> Optional[Course]:
		return self.repository.restore(course_id)

	def get_course_by_id(self, course_id: int) -> Optional[Course]:
		return self.repository.get_by_id(course_id)

	def get_course_by_slug(self, slug: str) -> Optional[Course]:
		return self.repository.get_by_slug(slug)

	def list_courses(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Course], int]:
		"""Returns tuple of (courses, total_count)"""
		courses = self.repository.list_all(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
			limit=limit,
			offset=offset,
		)
		total = self.repository.count(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
		)
		return courses, total

	def get_public_course(self, slug: str) -> Optional[Course]:
		"""Get a course only if it's published"""
		course = self.repository.get_by_slug(slug)
		if course and course.is_published:
			return course
		return None

	def list_public_courses(
		self,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Course], int]:
		"""List only published courses"""
		return self.list_courses(
			include_hidden=False,
			include_deleted=False,
			limit=limit,
			offset=offset,
		)
