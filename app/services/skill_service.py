"""
Skill service containing business logic for skills domain.
"""
import re
import unicodedata
from typing import Optional

from app.domain.entities.skill import Skill
from app.domain.repositories.skill_repository import SkillRepository


class SkillService:
	def __init__(self, repository: SkillRepository) -> None:
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

	def create_skill(
		self,
		title: str,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
	) -> Skill:
		if not slug:
			slug = self._generate_slug(title)

		slug = self._ensure_unique_slug(slug)

		return self.repository.create(
			title=title,
			slug=slug,
			description=description,
			metadata=metadata,
			visible=visible,
			order=order,
		)

	def update_skill(
		self,
		skill_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
	) -> Optional[Skill]:
		existing = self.repository.get_by_id(skill_id)
		if not existing:
			return None

		if slug and slug != existing.slug:
			if self.repository.slug_exists(slug, skill_id):
				raise ValueError("slug_already_exists")

		return self.repository.update(
			skill_id=skill_id,
			title=title,
			slug=slug,
			description=description,
			metadata=metadata,
			visible=visible,
			order=order,
		)

	def delete_skill(self, skill_id: int, soft: bool = True) -> bool:
		return self.repository.delete(skill_id, soft)

	def restore_skill(self, skill_id: int) -> Optional[Skill]:
		return self.repository.restore(skill_id)

	def get_skill_by_id(self, skill_id: int) -> Optional[Skill]:
		return self.repository.get_by_id(skill_id)

	def get_skill_by_slug(self, slug: str) -> Optional[Skill]:
		return self.repository.get_by_slug(slug)

	def list_skills(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Skill], int]:
		"""Returns tuple of (skills, total_count)"""
		skills = self.repository.list_all(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
			limit=limit,
			offset=offset,
		)
		total = self.repository.count(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
		)
		return skills, total

	def get_public_skill(self, slug: str) -> Optional[Skill]:
		"""Get a skill only if it's published"""
		skill = self.repository.get_by_slug(slug)
		if skill and skill.is_published:
			return skill
		return None

	def list_public_skills(
		self,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Skill], int]:
		"""List only published skills"""
		return self.list_skills(
			include_hidden=False,
			include_deleted=False,
			limit=limit,
			offset=offset,
		)
