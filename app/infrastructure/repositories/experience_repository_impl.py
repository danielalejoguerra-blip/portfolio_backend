"""
Experience repository implementation with SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.content_base import ContentMetadata
from app.domain.entities.experience import Experience
from app.domain.repositories.experience_repository import ExperienceRepository
from app.infrastructure.database.models.experience_model import ExperienceModel


class ExperienceRepositoryImpl(ExperienceRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def _to_entity(self, model: ExperienceModel) -> Experience:
		"""Map ORM model to domain entity"""
		return Experience(
			id=model.id,
			title=model.title,
			slug=model.slug,
			description=model.description,
			content=model.content,
			company=model.company or "",
			company_url=model.company_url,
			company_logo_url=model.company_logo_url,
			location=model.location,
			employment_type=model.employment_type or "full_time",
			work_mode=model.work_mode,
			department=model.department,
			start_date=model.start_date,
			end_date=model.end_date,
			is_current=model.is_current or False,
			tech_stack=model.tech_stack or [],
			responsibilities=model.responsibilities or [],
			achievements=model.achievements or [],
			related_projects=model.related_projects or [],
			references=model.references or [],
			images=model.images or [],
			visible=model.visible,
			order=model.order,
			metadata=ContentMetadata(data=model.meta or {}),
			created_at=model.created_at,
			updated_at=model.updated_at,
			deleted_at=model.deleted_at,
			translations=model.translations or {},
		)

	def get_by_id(self, experience_id: int) -> Optional[Experience]:
		model = self.db.query(ExperienceModel).filter(ExperienceModel.id == experience_id).first()
		if not model:
			return None
		return self._to_entity(model)

	def get_by_slug(self, slug: str) -> Optional[Experience]:
		model = self.db.query(ExperienceModel).filter(ExperienceModel.slug == slug).first()
		if not model:
			return None
		return self._to_entity(model)

	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[Experience]:
		query = self.db.query(ExperienceModel)

		if not include_deleted:
			query = query.filter(ExperienceModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(ExperienceModel.visible == True)

		query = query.order_by(ExperienceModel.order.asc(), ExperienceModel.created_at.desc())

		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		return [self._to_entity(m) for m in query.all()]

	def count(self, include_hidden: bool = False, include_deleted: bool = False) -> int:
		query = self.db.query(ExperienceModel)

		if not include_deleted:
			query = query.filter(ExperienceModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(ExperienceModel.visible == True)

		return query.count()

	def create(
		self,
		title: str,
		slug: str,
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
		model = ExperienceModel(
			title=title, slug=slug, description=description, content=content,
			company=company, company_url=company_url, company_logo_url=company_logo_url,
			location=location, employment_type=employment_type, work_mode=work_mode,
			department=department, start_date=start_date, end_date=end_date,
			is_current=is_current, tech_stack=tech_stack or [],
			responsibilities=responsibilities or [], achievements=achievements or [],
			related_projects=related_projects or [], references=references or [],
			images=images or [], meta=metadata or {}, visible=visible, order=order,
			translations=translations or {},
		)
		self.db.add(model)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def update(
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
		model = self.db.query(ExperienceModel).filter(ExperienceModel.id == experience_id).first()
		if not model:
			return None

		for attr, val in [
			("title", title), ("slug", slug), ("description", description), ("content", content),
			("company", company), ("company_url", company_url),
			("company_logo_url", company_logo_url), ("location", location),
			("employment_type", employment_type), ("work_mode", work_mode),
			("department", department), ("start_date", start_date), ("end_date", end_date),
			("is_current", is_current), ("tech_stack", tech_stack),
			("responsibilities", responsibilities), ("achievements", achievements),
			("related_projects", related_projects), ("references", references),
			("images", images), ("visible", visible), ("order", order),
			("translations", translations),
		]:
			if val is not None:
				setattr(model, attr, val)
		if metadata is not None:
			model.meta = metadata

		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def delete(self, experience_id: int, soft: bool = True) -> bool:
		model = self.db.query(ExperienceModel).filter(ExperienceModel.id == experience_id).first()
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

	def restore(self, experience_id: int) -> Optional[Experience]:
		model = self.db.query(ExperienceModel).filter(ExperienceModel.id == experience_id).first()
		if not model:
			return None

		model.deleted_at = None
		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		query = self.db.query(ExperienceModel).filter(ExperienceModel.slug == slug)
		if exclude_id:
			query = query.filter(ExperienceModel.id != exclude_id)
		return query.first() is not None
