"""
Education service containing business logic for education domain.
"""
import re
import unicodedata
from typing import Optional

from app.domain.entities.education import Education
from app.domain.repositories.education_repository import EducationRepository


class EducationService:
	def __init__(self, repository: EducationRepository) -> None:
		self.repository = repository

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

	def create_education(
		self,
		title: str,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
	) -> Education:
		if not slug:
			slug = self._generate_slug(title)

		slug = self._ensure_unique_slug(slug)

		return self.repository.create(
			title=title,
			slug=slug,
			description=description,
			content=content,
			images=images,
			metadata=metadata,
			visible=visible,
			order=order,
		)

	def update_education(
		self,
		education_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
	) -> Optional[Education]:
		existing = self.repository.get_by_id(education_id)
		if not existing:
			return None

		if slug and slug != existing.slug:
			if self.repository.slug_exists(slug, education_id):
				raise ValueError("slug_already_exists")

		return self.repository.update(
			education_id=education_id,
			title=title,
			slug=slug,
			description=description,
			content=content,
			images=images,
			metadata=metadata,
			visible=visible,
			order=order,
		)

	def delete_education(self, education_id: int, soft: bool = True) -> bool:
		return self.repository.delete(education_id, soft)

	def restore_education(self, education_id: int) -> Optional[Education]:
		return self.repository.restore(education_id)

	def get_education_by_id(self, education_id: int) -> Optional[Education]:
		return self.repository.get_by_id(education_id)

	def get_education_by_slug(self, slug: str) -> Optional[Education]:
		return self.repository.get_by_slug(slug)

	def list_education(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Education], int]:
		"""Returns tuple of (education_entries, total_count)"""
		entries = self.repository.list_all(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
			limit=limit,
			offset=offset,
		)
		total = self.repository.count(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
		)
		return entries, total

	def get_public_education(self, slug: str) -> Optional[Education]:
		"""Get an education entry only if it's published"""
		education = self.repository.get_by_slug(slug)
		if education and education.is_published:
			return education
		return None

	def list_public_education(
		self,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Education], int]:
		"""List only published education entries"""
		return self.list_education(
			include_hidden=False,
			include_deleted=False,
			limit=limit,
			offset=offset,
		)
