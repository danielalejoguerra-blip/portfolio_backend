"""
Experience service containing business logic for experience domain.
"""
import re
import unicodedata
from typing import Optional

from app.domain.entities.experience import Experience
from app.domain.repositories.experience_repository import ExperienceRepository
from app.services.ai_translation_service import AITranslationService


class ExperienceService:
	def __init__(self, repository: ExperienceRepository, ai_translation_service: AITranslationService = None) -> None:
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

	def create_experience(
		self,
		title: str,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		company: str = "",
		company_url: Optional[str] = None,
		company_logo_url: Optional[str] = None,
		location: Optional[str] = None,
		employment_type: str = "full_time",
		work_mode: Optional[str] = None,
		department: Optional[str] = None,
		start_date=None,
		end_date=None,
		is_current: bool = False,
		tech_stack: Optional[list] = None,
		responsibilities: Optional[list] = None,
		achievements: Optional[list] = None,
		related_projects: Optional[list] = None,
		references: Optional[list] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
		translations: dict = None,
	) -> Experience:
		if not slug:
			slug = self._generate_slug(title)

		slug = self._ensure_unique_slug(slug)

		# Auto-translate if no manual translations provided
		if not translations and self.ai_translation_service:
			translations = self.ai_translation_service.translate_fields(
				domain="experience",
				fields={"title": title, "description": description, "content": content},
			)

		return self.repository.create(
			title=title,
			slug=slug,
			description=description,
			content=content,
			company=company,
			company_url=company_url,
			company_logo_url=company_logo_url,
			location=location,
			employment_type=employment_type,
			work_mode=work_mode,
			department=department,
			start_date=start_date,
			end_date=end_date,
			is_current=is_current,
			tech_stack=tech_stack,
			responsibilities=responsibilities,
			achievements=achievements,
			related_projects=related_projects,
			references=references,
			images=images,
			metadata=metadata,
			visible=visible,
			order=order,
			translations=translations,
		)

	def update_experience(
		self,
		experience_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		company: Optional[str] = None,
		company_url: Optional[str] = None,
		company_logo_url: Optional[str] = None,
		location: Optional[str] = None,
		employment_type: Optional[str] = None,
		work_mode: Optional[str] = None,
		department: Optional[str] = None,
		start_date=None,
		end_date=None,
		is_current: Optional[bool] = None,
		tech_stack: Optional[list] = None,
		responsibilities: Optional[list] = None,
		achievements: Optional[list] = None,
		related_projects: Optional[list] = None,
		references: Optional[list] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
		translations: dict = None,
	) -> Optional[Experience]:
		existing = self.repository.get_by_id(experience_id)
		if not existing:
			return None

		if slug and slug != existing.slug:
			if self.repository.slug_exists(slug, experience_id):
				raise ValueError("slug_already_exists")

		# Auto-translate if no manual translations provided
		if translations is None and self.ai_translation_service:
			translate_fields = {
				"title": title if title is not None else existing.title,
				"description": description if description is not None else existing.description,
				"content": content if content is not None else existing.content,
			}
			translations = self.ai_translation_service.translate_fields(
				domain="experience",
				fields=translate_fields,
				existing_translations=existing.translations,
			)

		return self.repository.update(
			experience_id=experience_id,
			title=title,
			slug=slug,
			description=description,
			content=content,
			company=company,
			company_url=company_url,
			company_logo_url=company_logo_url,
			location=location,
			employment_type=employment_type,
			work_mode=work_mode,
			department=department,
			start_date=start_date,
			end_date=end_date,
			is_current=is_current,
			tech_stack=tech_stack,
			responsibilities=responsibilities,
			achievements=achievements,
			related_projects=related_projects,
			references=references,
			images=images,
			metadata=metadata,
			visible=visible,
			order=order,
			translations=translations,
		)

	def delete_experience(self, experience_id: int, soft: bool = True) -> bool:
		return self.repository.delete(experience_id, soft)

	def restore_experience(self, experience_id: int) -> Optional[Experience]:
		return self.repository.restore(experience_id)

	def get_experience_by_id(self, experience_id: int) -> Optional[Experience]:
		return self.repository.get_by_id(experience_id)

	def get_experience_by_slug(self, slug: str) -> Optional[Experience]:
		return self.repository.get_by_slug(slug)

	def list_experiences(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Experience], int]:
		"""Returns tuple of (experiences, total_count)"""
		experiences = self.repository.list_all(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
			limit=limit,
			offset=offset,
		)
		total = self.repository.count(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
		)
		return experiences, total

	def get_public_experience(self, slug: str) -> Optional[Experience]:
		"""Get an experience only if it's published"""
		experience = self.repository.get_by_slug(slug)
		if experience and experience.is_published:
			return experience
		return None

	def list_public_experiences(
		self,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Experience], int]:
		"""List only published experiences"""
		return self.list_experiences(
			include_hidden=False,
			include_deleted=False,
			limit=limit,
			offset=offset,
		)
