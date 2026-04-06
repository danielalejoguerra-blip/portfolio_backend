import logging
from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie
from typing import Any, Optional

import socketio
from jose import JWTError

logger = logging.getLogger(__name__)

from app.core import security
from app.core.config import settings
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl

analytics_namespace = settings.SOCKETIO_NAMESPACE_ANALYTICS
analytics_room = settings.SOCKETIO_ANALYTICS_ROOM

blog_namespace = settings.SOCKETIO_NAMESPACE_BLOG
blog_room = settings.SOCKETIO_BLOG_ROOM


def _build_manager() -> Optional[socketio.AsyncRedisManager]:
	if not settings.SOCKETIO_REDIS_URL:
		return None
	return socketio.AsyncRedisManager(settings.SOCKETIO_REDIS_URL)


def _parse_access_token(environ: dict[str, Any]) -> Optional[str]:
	cookie_header = environ.get("HTTP_COOKIE")
	if not cookie_header:
		return None

	cookie = SimpleCookie()
	cookie.load(cookie_header)
	token = cookie.get(settings.COOKIE_ACCESS_NAME)
	if not token:
		return None
	return token.value


def _get_authenticated_user(environ: dict[str, Any]):
	token = _parse_access_token(environ)
	if not token:
		logger.warning("Socket auth failed: no access_token cookie. HTTP_COOKIE=%s", environ.get("HTTP_COOKIE"))
		return None

	try:
		payload = security.decode_token(token)
		if payload.get("type") != "access":
			logger.warning("Socket auth failed: token type is '%s', expected 'access'", payload.get("type"))
			return None
		user_id = int(payload.get("sub"))
	except (JWTError, ValueError, TypeError) as e:
		logger.warning("Socket auth failed: token decode error: %s", e)
		return None

	db = SessionLocal()
	try:
		repository = UserRepositoryImpl(db)
		user = repository.get_by_id(user_id)
		if not user or not user.is_active:
			logger.warning("Socket auth failed: user_id=%s not found or inactive", user_id)
			return None
		return user
	finally:
		db.close()


socket_server = socketio.AsyncServer(
	async_mode="asgi",
	cors_allowed_origins=settings.BACKEND_CORS_ORIGINS or "*",
	client_manager=_build_manager(),
)


@socket_server.event(namespace=analytics_namespace)
async def connect(sid: str, environ: dict[str, Any], auth: Optional[dict[str, Any]]):
	_ = auth
	user = _get_authenticated_user(environ)
	if not user:
		return False

	await socket_server.save_session(sid, {"user_id": user.id}, namespace=analytics_namespace)
	await socket_server.enter_room(sid, analytics_room, namespace=analytics_namespace)
	return True


@socket_server.event(namespace=analytics_namespace)
async def disconnect(sid: str):
	await socket_server.leave_room(sid, analytics_room, namespace=analytics_namespace)


# ── Blog namespace (authenticated admin only) ─────────────────────────────────

@socket_server.event(namespace=blog_namespace)
async def connect(sid: str, environ: dict[str, Any], auth: Optional[dict[str, Any]]):  # noqa: F811
	_ = auth
	user = _get_authenticated_user(environ)
	if not user:
		return False

	await socket_server.save_session(sid, {"user_id": user.id}, namespace=blog_namespace)
	await socket_server.enter_room(sid, blog_room, namespace=blog_namespace)
	return True


@socket_server.event(namespace=blog_namespace)
async def disconnect(sid: str):  # noqa: F811
	await socket_server.leave_room(sid, blog_room, namespace=blog_namespace)


async def emit_blog_event(event: str, payload: dict[str, Any]) -> None:
	"""Emit a blog event to all authenticated admin clients.

	Events emitted:
	  - ``blog:created``   – A new post was created.
	  - ``blog:updated``   – An existing post was updated.
	  - ``blog:deleted``   – A post was (soft-)deleted.
	  - ``blog:restored``  – A soft-deleted post was restored.
	  - ``blog:published`` – Post status transitioned to *published*.
	  - ``blog:scheduled`` – Post status set to *scheduled*.
	"""
	await socket_server.emit(
		event,
		payload,
		namespace=blog_namespace,
		room=blog_room,
	)


async def emit_analytics_updates(
	event_payload: dict[str, Any],
	summary_payload: dict[str, Any],
	top_content_payload: dict[str, Any],
) -> None:
	await socket_server.emit(
		"analytics:event",
		event_payload,
		namespace=analytics_namespace,
		room=analytics_room,
	)
	await socket_server.emit(
		"analytics:summary",
		summary_payload,
		namespace=analytics_namespace,
		room=analytics_room,
	)
	await socket_server.emit(
		"analytics:top_content",
		top_content_payload,
		namespace=analytics_namespace,
		room=analytics_room,
	)


def _default_health_app(scope, receive, send):
	_ = scope
	_ = receive
	_ = send


def mount_socketio(fastapi_app):
	return socketio.ASGIApp(
		socketio_server=socket_server,
		other_asgi_app=fastapi_app,
		socketio_path=settings.SOCKETIO_PATH,
	)


def build_top_content_payload(items: list[dict[str, Any]], days: int) -> dict[str, Any]:
	end_date = datetime.now(timezone.utc)
	start_date = end_date - timedelta(days=days)
	return {
		"items": [
			{
				"content_type": item.get("content_type"),
				"content_id": item.get("content_id"),
				"view_count": item.get("views", 0),
			}
			for item in items
		],
		"period_start": start_date.isoformat(),
		"period_end": end_date.isoformat(),
	}
