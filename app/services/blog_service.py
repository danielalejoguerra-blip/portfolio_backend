"""
Blog service containing business logic for blog domain.
"""
import re
import unicodedata
from datetime import datetime
from typing import Optional

from app.domain.entities.blog import BlogPost
from app.domain.repositories.blog_repository import BlogRepository
from app.services.ai_translation_service import AITranslationService


class BlogService:
	def __init__(self, repository: BlogRepository, ai_translation_service: AITranslationService = None) -> None:
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

	def create_post(
		self,
		title: str,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		published_at: Optional[datetime] = None,
		translations: dict = None,
	) -> BlogPost:
		if not slug:
			slug = self._generate_slug(title)

		slug = self._ensure_unique_slug(slug)

		# Auto-translate if no manual translations provided
		if not translations and self.ai_translation_service:
			translations = self.ai_translation_service.translate_fields(
				domain="blog",
				fields={"title": title, "description": description, "content": content},
			)

		return self.repository.create(
			title=title,
			slug=slug,
			description=description,
			content=content,
			images=images,
			metadata=metadata,
			visible=visible,
			published_at=published_at,
			translations=translations,
		)

	def update_post(
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
		existing = self.repository.get_by_id(post_id)
		if not existing:
			return None

		if slug and slug != existing.slug:
			if self.repository.slug_exists(slug, post_id):
				raise ValueError("slug_already_exists")

		# Auto-translate if no manual translations provided
		if translations is None and self.ai_translation_service:
			translate_fields = {
				"title": title if title is not None else existing.title,
				"description": description if description is not None else existing.description,
				"content": content if content is not None else existing.content,
			}
			translations = self.ai_translation_service.translate_fields(
				domain="blog",
				fields=translate_fields,
				existing_translations=existing.translations,
			)

		return self.repository.update(
			post_id=post_id,
			title=title,
			slug=slug,
			description=description,
			content=content,
			images=images,
			metadata=metadata,
			visible=visible,
			published_at=published_at,
			translations=translations,
		)

	def delete_post(self, post_id: int, soft: bool = True) -> bool:
		return self.repository.delete(post_id, soft)

	def restore_post(self, post_id: int) -> Optional[BlogPost]:
		return self.repository.restore(post_id)

	def get_post_by_id(self, post_id: int) -> Optional[BlogPost]:
		return self.repository.get_by_id(post_id)

	def get_post_by_slug(self, slug: str) -> Optional[BlogPost]:
		return self.repository.get_by_slug(slug)

	def list_posts(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		include_scheduled: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[BlogPost], int]:
		"""Returns tuple of (posts, total_count)"""
		posts = self.repository.list_all(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
			include_scheduled=include_scheduled,
			limit=limit,
			offset=offset,
		)
		total = self.repository.count(
			include_hidden=include_hidden,
			include_deleted=include_deleted,
			include_scheduled=include_scheduled,
		)
		return posts, total

	def get_public_post(self, slug: str) -> Optional[BlogPost]:
		"""Get a post only if it's published"""
		post = self.repository.get_by_slug(slug)
		if post and post.is_published:
			return post
		return None

	def list_public_posts(
		self,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> tuple[list[BlogPost], int]:
		"""List only published posts"""
		return self.list_posts(
			include_hidden=False,
			include_deleted=False,
			include_scheduled=False,
			limit=limit,
			offset=offset,
		)
