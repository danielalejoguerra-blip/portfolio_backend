"""
Analytics API endpoints.
Public: POST endpoint for tracking events (lightweight, no auth)
Protected: GET endpoints for viewing analytics (require authentication)
"""
from datetime import datetime, timezone
import ipaddress
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import (
	get_analytics_service,
	get_blog_service,
	get_course_service,
	get_current_user,
	get_education_service,
	get_experience_service,
	get_project_service,
	get_skill_service,
)
from app.core.config import settings
from app.domain.schemas.analytics import (
	AnalyticsEventCreate,
	AnalyticsEventRead,
	AnalyticsSummaryRead,
	TopContentResponse,
	ViewsByDateResponse,
)
from app.infrastructure.realtime.socket_server import (
	build_top_content_payload,
	emit_analytics_updates,
)
from app.services.analytics_service import AnalyticsService
from app.services.blog_service import BlogService
from app.services.course_service import CourseService
from app.services.education_service import EducationService
from app.services.experience_service import ExperienceService
from app.services.project_service import ProjectService
from app.services.skill_service import SkillService

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_client_ip(request: Request) -> Optional[str]:
	"""Extract client IP from request, considering common reverse proxies/CDNs."""
	for header in ("CF-Connecting-IP", "X-Real-IP", "X-Forwarded-For"):
		value = request.headers.get(header)
		if value:
			if header == "X-Forwarded-For":
				return value.split(",")[0].strip()
			return value.strip()

	forwarded = request.headers.get("Forwarded")
	if forwarded:
		parts = [part.strip() for part in forwarded.split(";")]
		for part in parts:
			if part.lower().startswith("for="):
				return part.split("=", 1)[1].strip().strip('"').strip("[]")

	return request.client.host if request.client else None


def _normalize_page_slug(page_slug: str) -> str:
	"""Normalize incoming page_slug values to a route-like format."""
	parsed = urlparse(page_slug)
	path = parsed.path or page_slug
	cleaned = path.strip()
	if not cleaned:
		return "/"
	if not cleaned.startswith("/"):
		cleaned = f"/{cleaned}"
	if cleaned != "/":
		cleaned = cleaned.rstrip("/")
	return cleaned


def _resolve_country(request: Optional[Request], client_ip: Optional[str]) -> str:
	"""Resolve country as ISO alpha-2 with safe fallbacks for DB compatibility."""
	if request:
		for header in ("CF-IPCountry", "X-Country-Code", "X-Country"):
			country = request.headers.get(header)
			if country and country.strip():
				normalized = country.strip().upper()
				if len(normalized) == 2 and normalized.isalpha():
					return normalized
				if normalized in {"UNKNOWN", "UN"}:
					return "XX"

	if not client_ip:
		return "XX"

	try:
		ip_obj = ipaddress.ip_address(client_ip)
		if (
			ip_obj.is_private
			or ip_obj.is_loopback
			or ip_obj.is_link_local
			or ip_obj.is_reserved
			or ip_obj.is_unspecified
		):
			return "XL"
	except ValueError:
		return "XX"

	return "XX"


def _infer_content_from_page_slug(
	page_slug: str,
	project_service: ProjectService,
	blog_service: BlogService,
	course_service: CourseService,
	education_service: EducationService,
	experience_service: ExperienceService,
	skill_service: SkillService,
) -> tuple[Optional[str], Optional[int]]:
	"""Infer content_type/content_id from known public detail routes."""
	normalized_slug = _normalize_page_slug(page_slug)
	parts = [part for part in normalized_slug.strip("/").split("/") if part]
	if len(parts) != 2:
		return None, None

	section, entity_slug = parts[0], parts[1]
	if section == "projects":
		item = project_service.get_public_project(entity_slug)
		return ("project", item.id) if item else (None, None)
	if section == "blog":
		item = blog_service.get_public_post(entity_slug)
		return ("blog", item.id) if item else (None, None)
	if section == "courses":
		item = course_service.get_public_course(entity_slug)
		return ("course", item.id) if item else (None, None)
	if section == "education":
		item = education_service.get_public_education(entity_slug)
		return ("education", item.id) if item else (None, None)
	if section == "experience":
		item = experience_service.get_public_experience(entity_slug)
		return ("experience", item.id) if item else (None, None)
	if section == "skills":
		item = skill_service.get_public_skill(entity_slug)
		return ("skill", item.id) if item else (None, None)

	return None, None


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


def _summary_to_read(summary) -> dict:
	return {
		"total_page_views": summary.total_page_views,
		"unique_visitors": summary.unique_visitors,
		"top_pages": summary.top_pages,
		"top_referrers": summary.top_referrers,
		"views_by_country": summary.views_by_country,
		"views_by_date": summary.views_by_date,
		"period_start": summary.period_start,
		"period_end": summary.period_end,
	}


async def _emit_realtime_analytics(event_payload: dict, service: AnalyticsService) -> None:
	"""Emit realtime analytics updates to admin dashboard clients."""
	days = settings.ANALYTICS_REALTIME_DAYS
	limit = settings.ANALYTICS_REALTIME_TOP_LIMIT
	summary = service.get_summary(days=days)
	top_content_items = service.get_top_content(days=days, limit=limit)
	await emit_analytics_updates(
		event_payload=event_payload,
		summary_payload=_summary_to_read(summary),
		top_content_payload=build_top_content_payload(top_content_items, days=days),
	)


# ============================================================================
# Public Endpoints (For tracking - no auth required)
# ============================================================================

@router.post("/track", response_model=AnalyticsEventRead, status_code=201)
async def track_event(
	payload: AnalyticsEventCreate,
	request: Request,
	service: AnalyticsService = Depends(get_analytics_service),
):
	"""
	Track an analytics event (public endpoint).
	Used by frontend to track page views and interactions.
	IP address is hashed for privacy.
	"""
	client_ip = _get_client_ip(request)
	country = _resolve_country(request, client_ip)
	event = service.track_event(
		event_type=payload.event_type,
		page_slug=payload.page_slug,
		content_type=payload.content_type,
		content_id=payload.content_id,
		referrer=payload.referrer or request.headers.get("Referer"),
		user_agent=request.headers.get("User-Agent"),
		ip_address=client_ip,
		country=country,
		metadata=payload.metadata,
	)
	event_payload = _event_to_read(event)
	await _emit_realtime_analytics(event_payload=event_payload, service=service)
	return event_payload


@router.post("/pageview", response_model=AnalyticsEventRead, status_code=201)
async def track_pageview(
	page_slug: str = Query(..., description="The page slug being viewed"),
	content_type: Optional[str] = Query(None, description="Type of content (project, blog, etc.)"),
	content_id: Optional[int] = Query(None, description="ID of the specific content"),
	request: Request = None,
	service: AnalyticsService = Depends(get_analytics_service),
	project_service: ProjectService = Depends(get_project_service),
	blog_service: BlogService = Depends(get_blog_service),
	course_service: CourseService = Depends(get_course_service),
	education_service: EducationService = Depends(get_education_service),
	experience_service: ExperienceService = Depends(get_experience_service),
	skill_service: SkillService = Depends(get_skill_service),
):
	"""
	Track a page view (public endpoint).
	Simplified endpoint for common page view tracking.
	"""
	resolved_content_type = content_type
	resolved_content_id = content_id
	if not resolved_content_type or resolved_content_id is None:
		inferred_type, inferred_id = _infer_content_from_page_slug(
			page_slug=page_slug,
			project_service=project_service,
			blog_service=blog_service,
			course_service=course_service,
			education_service=education_service,
			experience_service=experience_service,
			skill_service=skill_service,
		)
		resolved_content_type = resolved_content_type or inferred_type
		resolved_content_id = resolved_content_id if resolved_content_id is not None else inferred_id

	normalized_page_slug = _normalize_page_slug(page_slug)
	client_ip = _get_client_ip(request) if request else None
	country = _resolve_country(request, client_ip)
	event = service.track_page_view(
		page_slug=normalized_page_slug,
		content_type=resolved_content_type,
		content_id=resolved_content_id,
		referrer=request.headers.get("Referer") if request else None,
		user_agent=request.headers.get("User-Agent") if request else None,
		ip_address=client_ip,
		country=country,
	)
	event_payload = _event_to_read(event)
	await _emit_realtime_analytics(event_payload=event_payload, service=service)
	return event_payload


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
