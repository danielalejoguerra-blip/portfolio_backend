"""
Project service containing business logic for projects domain.
"""
import re
import unicodedata
from typing import Optional

from app.domain.entities.project import Project
from app.domain.repositories.project_repository import ProjectRepository


class ProjectService:
	def __init__(self, repository: ProjectRepository) -> None:
		self.repository = repository

	def _generate_slug(self, title: str) -> str:
		"""Generate URL-friendly slug from title"""
		# Normalize unicode and convert to lowercase
		slug = unicodedata.normalize("NFKD", title.lower())
		# Remove accents
		slug = slug.encode("ascii", "ignore").decode("ascii")
		# Replace spaces and special chars with hyphens
		slug = re.sub(r"[^a-z0-9]+", "-", slug)
		# Remove leading/trailing hyphens
		slug = slug.strip("-")
		# Collapse multiple hyphens
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

	def create_project(
		self,
		title: str,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
	) -> Project:
		# Generate slug from title if not provided
		if not slug:
			slug = self._generate_slug(title)

		# Ensure slug is unique
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

	def update_project(
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
	) -> Optional[Project]:
		# Check if project exists
		existing = self.repository.get_by_id(project_id)
		if not existing:
			return None

		# If slug is being updated, ensure it's unique
		if slug and slug != existing.slug:
			if self.repository.slug_exists(slug, project_id):
				raise ValueError("slug_already_exists")

		return self.repository.update(
			project_id=project_id,
			title=title,
			slug=slug,
			description=description,
			content=content,
			images=images,
			metadata=metadata,
			visible=visible,
			order=order,
		)

	def delete_project(self, project_id: int, soft: bool = True) -> bool:
		return self.repository.delete(project_id, soft)

	def restore_project(self, project_id: int) -> Optional[Project]:
		return self.repository.restore(project_id)

	def get_project_by_id(self, project_id: int) -> Optional[Project]:
		return self.repository.get_by_id(project_id)

	def get_project_by_slug(self, slug: str) -> Optional[Project]:
		return self.repository.get_by_slug(slug)

	def list_projects(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Project], int]:
		"""Returns tuple of (projects, total_count)"""
		projects = self.repository.list_all(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
			limit=limit,
			offset=offset,
		)
		total = self.repository.count(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
		)
		return projects, total

	def get_public_project(self, slug: str) -> Optional[Project]:
		"""Get a project only if it's published (visible and not deleted)"""
		project = self.repository.get_by_slug(slug)
		if project and project.is_published:
			return project
		return None

	def list_public_projects(
		self,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[Project], int]:
		"""List only published projects"""
		return self.list_projects(
			include_hidden=False,
			include_deleted=False,
			limit=limit,
			offset=offset,
		)
