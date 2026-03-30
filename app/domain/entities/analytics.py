"""
Analytics entity for tracking portfolio engagement.
Different structure from content entities - tracks events and metrics.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass(frozen=True)
class AnalyticsEvent:
	"""
	Analytics event entity for tracking page views and interactions.
	
	Event types:
	- page_view: visitor viewed a page
	- project_click: visitor clicked on a project
	- external_link: visitor clicked external link
	- contact_form: visitor submitted contact form
	- download: visitor downloaded a file
	"""
	id: int
	event_type: str
	page_slug: Optional[str]  # Which page/content triggered the event
	content_type: Optional[str]  # "project", "blog", "course", etc.
	content_id: Optional[int]  # Reference to specific content
	referrer: Optional[str]  # Traffic source
	user_agent: Optional[str]
	ip_hash: Optional[str]  # Hashed IP for privacy
	country: Optional[str]
	metadata: dict[str, Any]  # Additional event data
	created_at: datetime


@dataclass(frozen=True)
class AnalyticsSummary:
	"""
	Aggregated analytics data for dashboard display.
	"""
	total_page_views: int
	unique_visitors: int
	top_pages: list[dict[str, Any]]
	top_referrers: list[dict[str, Any]]
	views_by_country: dict[str, int]
	views_by_date: list[dict[str, Any]]
	period_start: datetime
	period_end: datetime
