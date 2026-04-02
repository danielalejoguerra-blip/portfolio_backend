"""
Blog post ORM model for database persistence.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.session import Base


class BlogPostModel(Base):
	__tablename__ = "blog_posts"

	# ── Identity ───────────────────────────────────────────────
	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(255), nullable=False)
	slug = Column(String(255), unique=True, index=True, nullable=False)
	description = Column(String(1000), nullable=True)
	content = Column(Text, nullable=True)
	# Structured content blocks with per-block image positioning
	content_blocks = Column(JSONB, default=list, nullable=False)

	# ── Cover image ─────────────────────────────────────────
	cover_image_url = Column(String(2048), nullable=True)
	cover_image_alt = Column(String(255), nullable=True)
	cover_image_position = Column(String(20), nullable=False, default="center")

	# ── Classification ───────────────────────────────────────
	category = Column(String(100), nullable=True, index=True)
	tags = Column(JSONB, default=list, nullable=False)
	series = Column(String(255), nullable=True, index=True)
	series_order = Column(Integer, nullable=True)

	# ── Reading experience ─────────────────────────────────
	reading_time_minutes = Column(Integer, nullable=True)
	featured = Column(Boolean, default=False, nullable=False, index=True)

	# ── SEO ─────────────────────────────────────────────────
	seo_title = Column(String(60), nullable=True)
	seo_description = Column(String(160), nullable=True)
	canonical_url = Column(String(2048), nullable=True)
	og_image_url = Column(String(2048), nullable=True)

	# ── Media & publishing ─────────────────────────────────
	images = Column(JSONB, default=list, nullable=False)
	visible = Column(Boolean, default=True, nullable=False, index=True)
	published_at = Column(DateTime(timezone=True), nullable=True, index=True)

	# ── Meta / i18n ─────────────────────────────────────────
	meta = Column("metadata", JSONB, default=dict, nullable=False)
	translations = Column(JSONB, default=dict, nullable=False)
	created_at = Column(
		DateTime(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		nullable=False,
	)
	updated_at = Column(
		DateTime(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		nullable=False,
	)
	deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

