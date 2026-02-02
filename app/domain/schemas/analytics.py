"""
Analytics Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AnalyticsEventCreate(BaseModel):
	"""Schema for recording a new analytics event"""
	event_type: str = Field(min_length=1, max_length=50)
	page_slug: Optional[str] = Field(None, max_length=255)
	content_type: Optional[str] = Field(None, max_length=50)
	content_id: Optional[int] = None
	referrer: Optional[str] = Field(None, max_length=2000)
	metadata: dict[str, Any] = Field(default_factory=dict)


class AnalyticsEventRead(BaseModel):
	"""Schema for analytics event response"""
	id: int
	event_type: str
	page_slug: Optional[str] = None
	content_type: Optional[str] = None
	content_id: Optional[int] = None
	referrer: Optional[str] = None
	country: Optional[str] = None
	metadata: dict[str, Any] = Field(default_factory=dict)
	created_at: datetime

	class Config:
		from_attributes = True


class AnalyticsSummaryRead(BaseModel):
	"""Schema for analytics summary response"""
	total_page_views: int
	unique_visitors: int
	top_pages: list[dict[str, Any]]
	top_referrers: list[dict[str, Any]]
	views_by_country: dict[str, int]
	views_by_date: list[dict[str, Any]]
	period_start: datetime
	period_end: datetime


class AnalyticsQueryParams(BaseModel):
	"""Query parameters for analytics data"""
	start_date: Optional[datetime] = None
	end_date: Optional[datetime] = None
	event_type: Optional[str] = None
	content_type: Optional[str] = None
	content_id: Optional[int] = None
	limit: int = Field(default=100, ge=1, le=1000)
	offset: int = Field(default=0, ge=0)


class TopContentItem(BaseModel):
	"""Item in top content list"""
	content_type: str
	content_id: int
	title: Optional[str] = None
	slug: Optional[str] = None
	view_count: int


class TopContentResponse(BaseModel):
	"""Response for top content endpoint"""
	items: list[TopContentItem]
	period_start: datetime
	period_end: datetime


class ViewsByDateItem(BaseModel):
	"""Item in views by date response"""
	date: str
	views: int
	unique_visitors: int


class ViewsByDateResponse(BaseModel):
	"""Response for views by date endpoint"""
	items: list[ViewsByDateItem]
	granularity: str
	period_start: datetime
	period_end: datetime
