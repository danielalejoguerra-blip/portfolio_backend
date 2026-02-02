"""
Analytics repository interface.
Defines contract for analytics data access operations.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from app.domain.entities.analytics import AnalyticsEvent, AnalyticsSummary


class AnalyticsRepository(ABC):
	@abstractmethod
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
		raise NotImplementedError()

	@abstractmethod
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
		raise NotImplementedError()

	@abstractmethod
	def get_summary(
		self,
		start_date: datetime,
		end_date: datetime,
	) -> AnalyticsSummary:
		raise NotImplementedError()

	@abstractmethod
	def get_page_views_count(
		self,
		page_slug: Optional[str] = None,
		start_date: Optional[datetime] = None,
		end_date: Optional[datetime] = None,
	) -> int:
		raise NotImplementedError()

	@abstractmethod
	def get_content_views_count(
		self,
		content_type: str,
		content_id: int,
		start_date: Optional[datetime] = None,
		end_date: Optional[datetime] = None,
	) -> int:
		raise NotImplementedError()

	@abstractmethod
	def get_top_content(
		self,
		content_type: Optional[str] = None,
		start_date: Optional[datetime] = None,
		end_date: Optional[datetime] = None,
		limit: int = 10,
	) -> list[dict[str, Any]]:
		raise NotImplementedError()

	@abstractmethod
	def get_views_by_date(
		self,
		start_date: datetime,
		end_date: datetime,
		granularity: str = "day",  # "hour", "day", "week", "month"
	) -> list[dict[str, Any]]:
		raise NotImplementedError()

	@abstractmethod
	def cleanup_old_events(self, before_date: datetime) -> int:
		"""Remove events older than specified date. Returns count of deleted events."""
		raise NotImplementedError()
