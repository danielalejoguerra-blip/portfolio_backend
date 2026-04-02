"""
Project service containing business logic for projects domain.
"""
import re
import unicodedata
from typing import Optional

from app.domain.entities.project import Project
from app.domain.repositories.project_repository import ProjectRepository
from app.services.ai_translation_service import AITranslationService


class ProjectService:
	def __init__(self, repository: ProjectRepository, ai_translation_service: AITranslationService = None) -> None:
		self.repository = repository
		self.ai_translation_service = ai_translation_service

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
		status: str = "completed",
		category: Optional[str] = None,
		role: Optional[str] = None,
		start_date=None,
		end_date=None,
		team_size: Optional[int] = None,
		client: Optional[str] = None,
		tech_stack: Optional[list] = None,
		project_url: Optional[str] = None,
		repository_url: Optional[str] = None,
		documentation_url: Optional[str] = None,
		case_study_url: Optional[str] = None,
		metrics: Optional[list] = None,
		features: Optional[list] = None,
		challenges: Optional[list] = None,
		images: Optional[list[str]] = None,
		featured: bool = False,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
		translations: dict = None,
	) -> Project:
		# Generate slug from title if not provided
		if not slug:
			slug = self._generate_slug(title)

		# Ensure slug is unique
		slug = self._ensure_unique_slug(slug)

		# Auto-translate if no manual translations provided
		if not translations and self.ai_translation_service:
			translations = self.ai_translation_service.translate_fields(
				domain="project",
				fields={"title": title, "description": description, "content": content},
			)

		return self.repository.create(
			title=title,
			slug=slug,
			description=description,
			content=content,
			status=status,
			category=category,
			role=role,
			start_date=start_date,
			end_date=end_date,
			team_size=team_size,
			client=client,
			tech_stack=tech_stack,
			project_url=project_url,
			repository_url=repository_url,
			documentation_url=documentation_url,
			case_study_url=case_study_url,
			metrics=metrics,
			features=features,
			challenges=challenges,
			images=images,
			featured=featured,
			metadata=metadata,
			visible=visible,
			order=order,
			translations=translations,
		)

	def update_project(
		self,
		project_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		status: Optional[str] = None,
		category: Optional[str] = None,
		role: Optional[str] = None,
		start_date=None,
		end_date=None,
		team_size: Optional[int] = None,
		client: Optional[str] = None,
		tech_stack: Optional[list] = None,
		project_url: Optional[str] = None,
		repository_url: Optional[str] = None,
		documentation_url: Optional[str] = None,
		case_study_url: Optional[str] = None,
		metrics: Optional[list] = None,
		features: Optional[list] = None,
		challenges: Optional[list] = None,
		images: Optional[list[str]] = None,
		featured: Optional[bool] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
		translations: dict = None,
	) -> Optional[Project]:
		# Check if project exists
		existing = self.repository.get_by_id(project_id)
		if not existing:
			return None

		# If slug is being updated, ensure it's unique
		if slug and slug != existing.slug:
			if self.repository.slug_exists(slug, project_id):
				raise ValueError("slug_already_exists")

		# Auto-translate if no manual translations provided
		if translations is None and self.ai_translation_service:
			translate_fields = {
				"title": title if title is not None else existing.title,
				"description": description if description is not None else existing.description,
				"content": content if content is not None else existing.content,
			}
			translations = self.ai_translation_service.translate_fields(
				domain="project",
				fields=translate_fields,
				existing_translations=existing.translations,
			)

		return self.repository.update(
			project_id=project_id,
			title=title,
			slug=slug,
			description=description,
			content=content,
			status=status,
			category=category,
			role=role,
			start_date=start_date,
			end_date=end_date,
			team_size=team_size,
			client=client,
			tech_stack=tech_stack,
			project_url=project_url,
			repository_url=repository_url,
			documentation_url=documentation_url,
			case_study_url=case_study_url,
			metrics=metrics,
			features=features,
			challenges=challenges,
			images=images,
			featured=featured,
			metadata=metadata,
			visible=visible,
			order=order,
			translations=translations,
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
