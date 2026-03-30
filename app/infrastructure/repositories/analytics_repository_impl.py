"""
Analytics repository implementation with SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.entities.analytics import AnalyticsEvent, AnalyticsSummary
from app.domain.repositories.analytics_repository import AnalyticsRepository
from app.infrastructure.database.models.analytics_model import AnalyticsEventModel


class AnalyticsRepositoryImpl(AnalyticsRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def _to_entity(self, model: AnalyticsEventModel) -> AnalyticsEvent:
		"""Map ORM model to domain entity"""
		return AnalyticsEvent(
			id=model.id,
			event_type=model.event_type,
			page_slug=model.page_slug,
			content_type=model.content_type,
			content_id=model.content_id,
			referrer=model.referrer,
			user_agent=model.user_agent,
			ip_hash=model.ip_hash,
			country=model.country,
			metadata=model.meta or {},
			created_at=model.created_at,
		)

	def record_event(
		self,
		event_type: str,
		page_slug: Optional[str] = None,
		content_type: Optional[str] = None,
		content_id: Optional[int] = None,
		referrer: Optional[str] = None,
		user_agent: Optional[str] = None,
		ip_hash: Optional[str] = None,
		country: Optional[str] = None,
		metadata: Optional[dict[str, Any]] = None,
	) -> AnalyticsEvent:
		model = AnalyticsEventModel(
			event_type=event_type,
			page_slug=page_slug,
			content_type=content_type,
			content_id=content_id,
			referrer=referrer,
			user_agent=user_agent,
			ip_hash=ip_hash,
			country=country,
			meta=metadata or {},
		)
		self.db.add(model)
		self.db.commit()
		self.db.refresh(model)
		return self._to_entity(model)

	def get_events(
		self,
		event_type: Optional[str] = None,
		content_type: Optional[str] = None,
		content_id: Optional[int] = None,
		start_date: Optional[datetime] = None,
		end_date: Optional[datetime] = None,
		limit: Optional[int] = None,
		offset: int = 0,
	) -> list[AnalyticsEvent]:
		query = self.db.query(AnalyticsEventModel)

		if event_type:
			query = query.filter(AnalyticsEventModel.event_type == event_type)
		if content_type:
			query = query.filter(AnalyticsEventModel.content_type == content_type)
		if content_id:
			query = query.filter(AnalyticsEventModel.content_id == content_id)
		if start_date:
			query = query.filter(AnalyticsEventModel.created_at >= start_date)
		if end_date:
			query = query.filter(AnalyticsEventModel.created_at <= end_date)

		query = query.order_by(AnalyticsEventModel.created_at.desc())

		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		return [self._to_entity(m) for m in query.all()]

	def get_summary(
		self,
		start_date: datetime,
		end_date: datetime,
	) -> AnalyticsSummary:
		# Total page views
		total_views = self.db.query(AnalyticsEventModel).filter(
			AnalyticsEventModel.event_type == "page_view",
			AnalyticsEventModel.created_at >= start_date,
			AnalyticsEventModel.created_at <= end_date,
		).count()

		# Unique visitors (by ip_hash)
		unique_visitors = self.db.query(func.count(func.distinct(AnalyticsEventModel.ip_hash))).filter(
			AnalyticsEventModel.event_type == "page_view",
			AnalyticsEventModel.created_at >= start_date,
			AnalyticsEventModel.created_at <= end_date,
			AnalyticsEventModel.ip_hash.isnot(None),
		).scalar() or 0

		# Top pages
		top_pages_query = self.db.query(
			AnalyticsEventModel.page_slug,
			func.count(AnalyticsEventModel.id).label("views")
		).filter(
			AnalyticsEventModel.event_type == "page_view",
			AnalyticsEventModel.created_at >= start_date,
			AnalyticsEventModel.created_at <= end_date,
			AnalyticsEventModel.page_slug.isnot(None),
		).group_by(AnalyticsEventModel.page_slug).order_by(func.count(AnalyticsEventModel.id).desc()).limit(10).all()

		top_pages = [{"page": p[0], "views": p[1]} for p in top_pages_query]

		# Top referrers
		top_referrers_query = self.db.query(
			AnalyticsEventModel.referrer,
			func.count(AnalyticsEventModel.id).label("count")
		).filter(
			AnalyticsEventModel.created_at >= start_date,
			AnalyticsEventModel.created_at <= end_date,
			AnalyticsEventModel.referrer.isnot(None),
			AnalyticsEventModel.referrer != "",
		).group_by(AnalyticsEventModel.referrer).order_by(func.count(AnalyticsEventModel.id).desc()).limit(10).all()

		top_referrers = [{"referrer": r[0], "count": r[1]} for r in top_referrers_query]

		# Views by country
		country_query = self.db.query(
			AnalyticsEventModel.country,
			func.count(AnalyticsEventModel.id).label("views")
		).filter(
			AnalyticsEventModel.event_type == "page_view",
			AnalyticsEventModel.created_at >= start_date,
			AnalyticsEventModel.created_at <= end_date,
			AnalyticsEventModel.country.isnot(None),
		).group_by(AnalyticsEventModel.country).all()

		views_by_country = {c[0]: c[1] for c in country_query}

		# Views by date (daily)
		views_by_date = self.get_views_by_date(start_date, end_date, "day")

		return AnalyticsSummary(
			total_page_views=total_views,
			unique_visitors=unique_visitors,
			top_pages=top_pages,
			top_referrers=top_referrers,
			views_by_country=views_by_country,
			views_by_date=views_by_date,
			period_start=start_date,
			period_end=end_date,
		)

	def get_page_views_count(
		self,
		page_slug: Optional[str] = None,
		start_date: Optional[datetime] = None,
		end_date: Optional[datetime] = None,
	) -> int:
		query = self.db.query(AnalyticsEventModel).filter(
			AnalyticsEventModel.event_type == "page_view"
		)

		if page_slug:
			query = query.filter(AnalyticsEventModel.page_slug == page_slug)
		if start_date:
			query = query.filter(AnalyticsEventModel.created_at >= start_date)
		if end_date:
			query = query.filter(AnalyticsEventModel.created_at <= end_date)

		return query.count()

	def get_content_views_count(
		self,
		content_type: str,
		content_id: int,
		start_date: Optional[datetime] = None,
		end_date: Optional[datetime] = None,
	) -> int:
		query = self.db.query(AnalyticsEventModel).filter(
			AnalyticsEventModel.event_type == "page_view",
			AnalyticsEventModel.content_type == content_type,
			AnalyticsEventModel.content_id == content_id,
		)

		if start_date:
			query = query.filter(AnalyticsEventModel.created_at >= start_date)
		if end_date:
			query = query.filter(AnalyticsEventModel.created_at <= end_date)

		return query.count()

	def get_top_content(
		self,
		content_type: Optional[str] = None,
		start_date: Optional[datetime] = None,
		end_date: Optional[datetime] = None,
		limit: int = 10,
	) -> list[dict[str, Any]]:
		query = self.db.query(
			AnalyticsEventModel.content_type,
			AnalyticsEventModel.content_id,
			func.count(AnalyticsEventModel.id).label("views")
		).filter(
			AnalyticsEventModel.event_type == "page_view",
			AnalyticsEventModel.content_type.isnot(None),
			AnalyticsEventModel.content_id.isnot(None),
		)

		if content_type:
			query = query.filter(AnalyticsEventModel.content_type == content_type)
		if start_date:
			query = query.filter(AnalyticsEventModel.created_at >= start_date)
		if end_date:
			query = query.filter(AnalyticsEventModel.created_at <= end_date)

		results = query.group_by(
			AnalyticsEventModel.content_type,
			AnalyticsEventModel.content_id
		).order_by(func.count(AnalyticsEventModel.id).desc()).limit(limit).all()

		return [
			{"content_type": r[0], "content_id": r[1], "views": r[2]}
			for r in results
		]

	def get_views_by_date(
		self,
		start_date: datetime,
		end_date: datetime,
		granularity: str = "day",
	) -> list[dict[str, Any]]:
		# Use date truncation based on granularity
		if granularity == "hour":
			date_trunc = func.date_trunc("hour", AnalyticsEventModel.created_at)
		elif granularity == "week":
			date_trunc = func.date_trunc("week", AnalyticsEventModel.created_at)
		elif granularity == "month":
			date_trunc = func.date_trunc("month", AnalyticsEventModel.created_at)
		else:  # day (default)
			date_trunc = func.date_trunc("day", AnalyticsEventModel.created_at)

		results = self.db.query(
			date_trunc.label("date"),
			func.count(AnalyticsEventModel.id).label("views"),
			func.count(func.distinct(AnalyticsEventModel.ip_hash)).label("unique_visitors")
		).filter(
			AnalyticsEventModel.event_type == "page_view",
			AnalyticsEventModel.created_at >= start_date,
			AnalyticsEventModel.created_at <= end_date,
		).group_by(date_trunc).order_by(date_trunc).all()

		return [
			{
				"date": r[0].isoformat() if r[0] else None,
				"views": r[1],
				"unique_visitors": r[2]
			}
			for r in results
		]

	def cleanup_old_events(self, before_date: datetime) -> int:
		"""Remove events older than specified date"""
		result = self.db.query(AnalyticsEventModel).filter(
			AnalyticsEventModel.created_at < before_date
		).delete(synchronize_session=False)
		self.db.commit()
		return result
