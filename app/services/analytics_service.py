"""
Analytics service containing business logic for analytics domain.
"""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app.domain.entities.analytics import AnalyticsEvent, AnalyticsSummary
from app.domain.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
	def __init__(self, repository: AnalyticsRepository) -> None:
		self.repository = repository

	def _hash_ip(self, ip: str) -> str:
		"""Hash IP address for privacy - one-way hash with daily salt"""
		# Use date as salt so hashes change daily (privacy)
		salt = datetime.now(timezone.utc).strftime("%Y-%m-%d")
		return hashlib.sha256(f"{ip}:{salt}".encode()).hexdigest()

	def track_page_view(
		self,
		page_slug: str,
		content_type: Optional[str] = None,
		content_id: Optional[int] = None,
		referrer: Optional[str] = None,
		user_agent: Optional[str] = None,
		ip_address: Optional[str] = None,
		country: Optional[str] = None,
		metadata: Optional[dict[str, Any]] = None,
	) -> AnalyticsEvent:
		"""Track a page view event"""
		ip_hash = self._hash_ip(ip_address) if ip_address else None

		return self.repository.record_event(
			event_type="page_view",
			page_slug=page_slug,
			content_type=content_type,
			content_id=content_id,
			referrer=referrer,
			user_agent=user_agent,
			ip_hash=ip_hash,
			country=country,
			metadata=metadata,
		)

	def track_event(
		self,
		event_type: str,
		page_slug: Optional[str] = None,
		content_type: Optional[str] = None,
		content_id: Optional[int] = None,
		referrer: Optional[str] = None,
		user_agent: Optional[str] = None,
		ip_address: Optional[str] = None,
		country: Optional[str] = None,
		metadata: Optional[dict[str, Any]] = None,
	) -> AnalyticsEvent:
		"""Track a custom event"""
		ip_hash = self._hash_ip(ip_address) if ip_address else None

		return self.repository.record_event(
			event_type=event_type,
			page_slug=page_slug,
			content_type=content_type,
			content_id=content_id,
			referrer=referrer,
			user_agent=user_agent,
			ip_hash=ip_hash,
			country=country,
			metadata=metadata,
		)

	def get_summary(
		self,
		days: int = 30,
		start_date: Optional[datetime] = None,
		end_date: Optional[datetime] = None,
	) -> AnalyticsSummary:
		"""Get analytics summary for a period"""
		if not end_date:
			end_date = datetime.now(timezone.utc)
		if not start_date:
			start_date = end_date - timedelta(days=days)

		return self.repository.get_summary(start_date, end_date)

	def get_page_views(
		self,
		page_slug: Optional[str] = None,
		days: int = 30,
	) -> int:
		"""Get page view count for a specific page or all pages"""
		end_date = datetime.now(timezone.utc)
		start_date = end_date - timedelta(days=days)

		return self.repository.get_page_views_count(
			page_slug=page_slug,
			start_date=start_date,
			end_date=end_date,
		)

	def get_content_views(
		self,
		content_type: str,
		content_id: int,
		days: int = 30,
	) -> int:
		"""Get view count for specific content"""
		end_date = datetime.now(timezone.utc)
		start_date = end_date - timedelta(days=days)

		return self.repository.get_content_views_count(
			content_type=content_type,
			content_id=content_id,
			start_date=start_date,
			end_date=end_date,
		)

	def get_top_content(
		self,
		content_type: Optional[str] = None,
		days: int = 30,
		limit: int = 10,
	) -> list[dict[str, Any]]:
		"""Get top viewed content"""
		end_date = datetime.now(timezone.utc)
		start_date = end_date - timedelta(days=days)

		return self.repository.get_top_content(
			content_type=content_type,
			start_date=start_date,
			end_date=end_date,
			limit=limit,
		)

	def get_views_by_date(
		self,
		days: int = 30,
		granularity: str = "day",
	) -> list[dict[str, Any]]:
		"""Get views grouped by date"""
		end_date = datetime.now(timezone.utc)
		start_date = end_date - timedelta(days=days)

		return self.repository.get_views_by_date(
			start_date=start_date,
			end_date=end_date,
			granularity=granularity,
		)

	def get_events(
		self,
		event_type: Optional[str] = None,
		content_type: Optional[str] = None,
		content_id: Optional[int] = None,
		days: int = 30,
		limit: int = 100,
		offset: int = 0,
	) -> list[AnalyticsEvent]:
		"""Get analytics events with filters"""
		end_date = datetime.now(timezone.utc)
		start_date = end_date - timedelta(days=days)

		return self.repository.get_events(
			event_type=event_type,
			content_type=content_type,
			content_id=content_id,
			start_date=start_date,
			end_date=end_date,
			limit=limit,
			offset=offset,
		)

	def cleanup_old_data(self, days: int = 365) -> int:
		"""Remove analytics data older than specified days"""
		cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
		return self.repository.cleanup_old_events(cutoff_date)
