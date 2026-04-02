"""
Education repository implementation with SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.content_base import ContentMetadata
from app.domain.entities.education import Education
from app.domain.repositories.education_repository import EducationRepository
from app.infrastructure.database.models.education_model import EducationModel


class EducationRepositoryImpl(EducationRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def _to_entity(self, model: EducationModel) -> Education:
		"""Map ORM model to domain entity"""
		return Education(
			id=model.id,
			title=model.title,
			slug=model.slug,
			description=model.description,
			content=model.content,
			institution=model.institution or "",
			institution_url=model.institution_url,
			location=model.location,
			degree_type=model.degree_type or "bachelor",
			field_of_study=model.field_of_study,
			start_date=model.start_date,
			end_date=model.end_date,
			credential_id=model.credential_id,
			credential_url=model.credential_url,
			grade=model.grade,
			honors=model.honors,
			relevant_coursework=model.relevant_coursework or [],
			activities=model.activities or [],
			achievements=model.achievements or [],
			images=model.images or [],
			visible=model.visible,
			order=model.order,
			metadata=ContentMetadata(data=model.meta or {}),
			created_at=model.created_at,
			updated_at=model.updated_at,
			deleted_at=model.deleted_at,
			translations=model.translations or {},
		)

	def get_by_id(self, education_id: int) -> Optional[Education]:
		model = self.db.query(EducationModel).filter(EducationModel.id == education_id).first()
		if not model:
			return None
		return self._to_entity(model)

	def get_by_slug(self, slug: str) -> Optional[Education]:
		model = self.db.query(EducationModel).filter(EducationModel.slug == slug).first()
		if not model:
			return None
		return self._to_entity(model)

	def list_all(
		self,
		include_hidden: bool = False,
		include_deleted: bool = False,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[Education]:
		query = self.db.query(EducationModel)

		if not include_deleted:
			query = query.filter(EducationModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(EducationModel.visible == True)

		query = query.order_by(EducationModel.order.asc(), EducationModel.created_at.desc())

		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		return [self._to_entity(m) for m in query.all()]

	def count(self, include_hidden: bool = False, include_deleted: bool = False) -> int:
		query = self.db.query(EducationModel)

		if not include_deleted:
			query = query.filter(EducationModel.deleted_at.is_(None))
		if not include_hidden:
			query = query.filter(EducationModel.visible == True)

		return query.count()

	def create(
		self,
		title: str,
		slug: str,
		description: Optional[str] = None,
		content: Optional[str] = None,
		institution: str = "",
		institution_url: Optional[str] = None,
		location: Optional[str] = None,
		degree_type: str = "bachelor",
		field_of_study: Optional[str] = None,
		start_date=None,
		end_date=None,
		credential_id: Optional[str] = None,
		credential_url: Optional[str] = None,
		grade: Optional[str] = None,
		honors: Optional[str] = None,
		relevant_coursework: Optional[list] = None,
		activities: Optional[list] = None,
		achievements: Optional[list] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: bool = True,
		order: int = 0,
		translations: dict = None,
	) -> Education:
		model = EducationModel(
			title=title,
			slug=slug,
			description=description,
			content=content,
			institution=institution,
			institution_url=institution_url,
			location=location,
			degree_type=degree_type,
			field_of_study=field_of_study,
			start_date=start_date,
			end_date=end_date,
			credential_id=credential_id,
			credential_url=credential_url,
			grade=grade,
			honors=honors,
			relevant_coursework=relevant_coursework or [],
			activities=activities or [],
			achievements=achievements or [],
			images=images or [],
			meta=metadata or {},
			visible=visible,
			order=order,
			translations=translations or {},
		)
		self.db.add(model)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def update(
		self,
		education_id: int,
		title: Optional[str] = None,
		slug: Optional[str] = None,
		description: Optional[str] = None,
		content: Optional[str] = None,
		institution: Optional[str] = None,
		institution_url: Optional[str] = None,
		location: Optional[str] = None,
		degree_type: Optional[str] = None,
		field_of_study: Optional[str] = None,
		start_date=None,
		end_date=None,
		credential_id: Optional[str] = None,
		credential_url: Optional[str] = None,
		grade: Optional[str] = None,
		honors: Optional[str] = None,
		relevant_coursework: Optional[list] = None,
		activities: Optional[list] = None,
		achievements: Optional[list] = None,
		images: Optional[list[str]] = None,
		metadata: Optional[dict] = None,
		visible: Optional[bool] = None,
		order: Optional[int] = None,
		translations: dict = None,
	) -> Optional[Education]:
		model = self.db.query(EducationModel).filter(EducationModel.id == education_id).first()
		if not model:
			return None

		for attr, val in [
			("title", title), ("slug", slug), ("description", description),
			("content", content), ("institution", institution),
			("institution_url", institution_url), ("location", location),
			("degree_type", degree_type), ("field_of_study", field_of_study),
			("start_date", start_date), ("end_date", end_date),
			("credential_id", credential_id), ("credential_url", credential_url),
			("grade", grade), ("honors", honors),
			("relevant_coursework", relevant_coursework),
			("activities", activities), ("achievements", achievements),
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

	def delete(self, education_id: int, soft: bool = True) -> bool:
		model = self.db.query(EducationModel).filter(EducationModel.id == education_id).first()
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

	def restore(self, education_id: int) -> Optional[Education]:
		model = self.db.query(EducationModel).filter(EducationModel.id == education_id).first()
		if not model:
			return None

		model.deleted_at = None
		model.updated_at = datetime.now(timezone.utc)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
		query = self.db.query(EducationModel).filter(EducationModel.slug == slug)
		if exclude_id:
			query = query.filter(EducationModel.id != exclude_id)
		return query.first() is not None
