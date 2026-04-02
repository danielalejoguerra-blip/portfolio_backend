"""
Project repository implementation with SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.content_base import ContentMetadata
from app.domain.entities.project import Project
from app.domain.repositories.project_repository import ProjectRepository
from app.infrastructure.database.models.project_model import ProjectModel


class ProjectRepositoryImpl(ProjectRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def _to_entity(self, model: ProjectModel) -> Project:
		"""Map ORM model to domain entity"""
		return Project(
			id=model.id,
			title=model.title,
			slug=model.slug,
			description=model.description,
			content=model.content,
			status=model.status or "completed",
			category=model.category,
			role=model.role,
			start_date=model.start_date,
			end_date=model.end_date,
			team_size=model.team_size,
			client=model.client,
			tech_stack=model.tech_stack or [],
			project_url=model.project_url,
			repository_url=model.repository_url,
			documentation_url=model.documentation_url,
			case_study_url=model.case_study_url,
			metrics=model.metrics or [],
			features=model.features or [],
			challenges=model.challenges or [],
			images=model.images or [],
			featured=model.featured or False,
			visible=model.visible,
			order=model.order,
			metadata=ContentMetadata(data=model.meta or {}),
			created_at=model.created_at,
			updated_at=model.updated_at,
			deleted_at=model.deleted_at,
			translations=model.translations or {},
		)

	def get_by_id(self, project_id: int) -> Optional[Project]:
		model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
		if not model:
			return None
		return self._to_entity(model)

	def get_by_slug(self, slug: str) -> Optional[Project]:
		model = self.db.query(ProjectModel).filter(ProjectModel.slug == slug).first()
		if not model:
			return None
		return self._to_entity(model)

	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[Project]:
		query = self.db.query(ProjectModel)

		if not include_deleted:
			query = query.filter(ProjectModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(ProjectModel.visible == True)

		query = query.order_by(ProjectModel.order.asc(), ProjectModel.created_at.desc())

		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		return [self._to_entity(m) for m in query.all()]

	def count(self, include_hidden: bool = False, include_deleted: bool = False) -> int:
		query = self.db.query(ProjectModel)

		if not include_deleted:
			query = query.filter(ProjectModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(ProjectModel.visible == True)

		return query.count()

	def create(
		self,
		title: str,
		slug: str,
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
		model = ProjectModel(
			title=title, slug=slug, description=description, content=content,
			status=status, category=category, role=role,
			start_date=start_date, end_date=end_date,
			team_size=team_size, client=client,
			tech_stack=tech_stack or [],
			project_url=project_url, repository_url=repository_url,
			documentation_url=documentation_url, case_study_url=case_study_url,
			metrics=metrics or [], features=features or [], challenges=challenges or [],
			images=images or [], featured=featured,
			meta=metadata or {}, visible=visible, order=order,
			translations=translations or {},
		)
		self.db.add(model)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def update(
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
		model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
		if not model:
			return None

		for attr, val in [
			("title", title), ("slug", slug), ("description", description), ("content", content),
			("status", status), ("category", category), ("role", role),
			("start_date", start_date), ("end_date", end_date),
			("team_size", team_size), ("client", client),
			("tech_stack", tech_stack), ("project_url", project_url),
			("repository_url", repository_url), ("documentation_url", documentation_url),
			("case_study_url", case_study_url), ("metrics", metrics),
			("features", features), ("challenges", challenges),
			("images", images), ("featured", featured),
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

	def delete(self, project_id: int, soft: bool = True) -> bool:
		model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
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

	def restore(self, project_id: int) -> Optional[Project]:
		model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
		if not model:
			return None

		model.deleted_at = None
		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		query = self.db.query(ProjectModel).filter(ProjectModel.slug == slug)
		if exclude_id:
			query = query.filter(ProjectModel.id != exclude_id)
		return query.first() is not None
