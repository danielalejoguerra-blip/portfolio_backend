"""
Analytics API endpoints.
Public: POST endpoint for tracking events (lightweight, no auth)
Protected: GET endpoints for viewing analytics (require authentication)
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_analytics_service, get_current_user
from app.domain.schemas.analytics import (
	AnalyticsEventCreate,
	AnalyticsEventRead,
	AnalyticsSummaryRead,
	TopContentResponse,
	ViewsByDateResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_client_ip(request: Request) -> Optional[str]:
	"""Extract client IP from request, considering proxies"""
	forwarded = request.headers.get("X-Forwarded-For")
	if forwarded:
		return forwarded.split(",")[0].strip()
	return request.client.host if request.client else None


def _event_to_read(event) -> dict:
	"""Convert domain entity to response dict"""
	return {
		"id": event.id,
		"event_type": event.event_type,
		"page_slug": event.page_slug,
		"content_type": event.content_type,
		"content_id": event.content_id,
		"referrer": event.referrer,
		"country": event.country,
		"metadata": event.metadata,
		"created_at": event.created_at,
	}


# ============================================================================
# Public Endpoints (For tracking - no auth required)
# ============================================================================

@router.post("/track", response_model=AnalyticsEventRead, status_code=201)
def track_event(
	payload: AnalyticsEventCreate,
	request: Request,
	service: AnalyticsService = Depends(get_analytics_service),
):
	"""
	Track an analytics event (public endpoint).
	Used by frontend to track page views and interactions.
	IP address is hashed for privacy.
	"""
	event = service.track_event(
		event_type=payload.event_type,
		page_slug=payload.page_slug,
		content_type=payload.content_type,
		content_id=payload.content_id,
		referrer=payload.referrer or request.headers.get("Referer"),
		user_agent=request.headers.get("User-Agent"),
		ip_address=_get_client_ip(request),
		metadata=payload.metadata,
	)
	return _event_to_read(event)


@router.post("/pageview", response_model=AnalyticsEventRead, status_code=201)
def track_pageview(
	page_slug: str = Query(..., description="The page slug being viewed"),
	content_type: Optional[str] = Query(None, description="Type of content (project, blog, etc.)"),
	content_id: Optional[int] = Query(None, description="ID of the specific content"),
	request: Request = None,
	service: AnalyticsService = Depends(get_analytics_service),
):
	"""
	Track a page view (public endpoint).
	Simplified endpoint for common page view tracking.
	"""
	event = service.track_page_view(
		page_slug=page_slug,
		content_type=content_type,
		content_id=content_id,
		referrer=request.headers.get("Referer") if request else None,
		user_agent=request.headers.get("User-Agent") if request else None,
		ip_address=_get_client_ip(request) if request else None,
	)
	return _event_to_read(event)


# ============================================================================
# Protected Endpoints (Admin only - for viewing analytics)
# ============================================================================

@router.get("/summary", response_model=AnalyticsSummaryRead)
def get_analytics_summary(
	days: int = Query(default=30, ge=1, le=365, description="Number of days to include"),
	_current_user=Depends(get_current_user),
	service: AnalyticsService = Depends(get_analytics_service),
):
	"""Get analytics summary for the specified period (admin only)"""
	summary = service.get_summary(days=days)
	return AnalyticsSummaryRead(
		total_page_views=summary.total_page_views,
		unique_visitors=summary.unique_visitors,
		top_pages=summary.top_pages,
		top_referrers=summary.top_referrers,
		views_by_country=summary.views_by_country,
		views_by_date=summary.views_by_date,
		period_start=summary.period_start,
		period_end=summary.period_end,
	)


@router.get("/top-content", response_model=TopContentResponse)
def get_top_content(
	content_type: Optional[str] = Query(None, description="Filter by content type"),
	days: int = Query(default=30, ge=1, le=365),
	limit: int = Query(default=10, ge=1, le=50),
	_current_user=Depends(get_current_user),
	service: AnalyticsService = Depends(get_analytics_service),
):
	"""Get top viewed content (admin only)"""
	from datetime import timedelta
	end_date = datetime.now(timezone.utc)
	start_date = end_date - timedelta(days=days)

	items = service.get_top_content(
		content_type=content_type,
		days=days,
		limit=limit,
	)
	return TopContentResponse(
		items=[
			{
				"content_type": item["content_type"],
				"content_id": item["content_id"],
				"view_count": item["views"],
			}
			for item in items
		],
		period_start=start_date,
		period_end=end_date,
	)


@router.get("/views-by-date", response_model=ViewsByDateResponse)
def get_views_by_date(
	days: int = Query(default=30, ge=1, le=365),
	granularity: str = Query(default="day", pattern="^(hour|day|week|month)$"),
	_current_user=Depends(get_current_user),
	service: AnalyticsService = Depends(get_analytics_service),
):
	"""Get page views grouped by date (admin only)"""
	from datetime import timedelta
	end_date = datetime.now(timezone.utc)
	start_date = end_date - timedelta(days=days)

	items = service.get_views_by_date(days=days, granularity=granularity)
	return ViewsByDateResponse(
		items=[
			{
				"date": item["date"],
				"views": item["views"],
				"unique_visitors": item["unique_visitors"],
			}
			for item in items
		],
		granularity=granularity,
		period_start=start_date,
		period_end=end_date,
	)


@router.get("/events", response_model=list[AnalyticsEventRead])
def get_events(
	event_type: Optional[str] = Query(None),
	content_type: Optional[str] = Query(None),
	content_id: Optional[int] = Query(None),
	days: int = Query(default=30, ge=1, le=365),
	limit: int = Query(default=100, ge=1, le=1000),
	offset: int = Query(default=0, ge=0),
	_current_user=Depends(get_current_user),
	service: AnalyticsService = Depends(get_analytics_service),
):
	"""Get raw analytics events with filters (admin only)"""
	events = service.get_events(
		event_type=event_type,
		content_type=content_type,
		content_id=content_id,
		days=days,
		limit=limit,
		offset=offset,
	)
	return [_event_to_read(e) for e in events]


@router.get("/page-views")
def get_page_views_count(
	page_slug: Optional[str] = Query(None, description="Filter by specific page"),
	days: int = Query(default=30, ge=1, le=365),
	_current_user=Depends(get_current_user),
	service: AnalyticsService = Depends(get_analytics_service),
):
	"""Get page view count (admin only)"""
	count = service.get_page_views(page_slug=page_slug, days=days)
	return {"page_slug": page_slug, "views": count, "days": days}


@router.get("/content-views/{content_type}/{content_id}")
def get_content_views_count(
	content_type: str,
	content_id: int,
	days: int = Query(default=30, ge=1, le=365),
	_current_user=Depends(get_current_user),
	service: AnalyticsService = Depends(get_analytics_service),
):
	"""Get view count for specific content (admin only)"""
	count = service.get_content_views(
		content_type=content_type,
		content_id=content_id,
		days=days,
	)
	return {
		"content_type": content_type,
		"content_id": content_id,
		"views": count,
		"days": days,
	}
