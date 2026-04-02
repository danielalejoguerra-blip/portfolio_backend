"""
Course ORM model for database persistence.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.session import Base


class CourseModel(Base):
	__tablename__ = "courses"

	# ── Identity ───────────────────────────────────────────────
	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(255), nullable=False)
	slug = Column(String(255), unique=True, index=True, nullable=False)
	description = Column(String(1000), nullable=True)
	content = Column(Text, nullable=True)

	# ── Classification ───────────────────────────────────────
	is_certification = Column(Boolean, default=False, nullable=False, index=True)
	category = Column(String(50), nullable=True, index=True)
	level = Column(String(20), nullable=True)

	# ── Platform ─────────────────────────────────────────────
	platform = Column(String(255), nullable=True, index=True)
	platform_url = Column(String(2048), nullable=True)
	instructor = Column(String(255), nullable=True)
	instructor_url = Column(String(2048), nullable=True)

	# ── Timeline ─────────────────────────────────────────────
	completion_date = Column(Date, nullable=True, index=True)
	expiration_date = Column(Date, nullable=True)
	duration_hours = Column(Integer, nullable=True)

	# ── Credential ─────────────────────────────────────────
	credential_id = Column(String(255), nullable=True)
	certificate_url = Column(String(2048), nullable=True)
	certificate_image_url = Column(String(2048), nullable=True)
	badge_url = Column(String(2048), nullable=True)

	# ── Learning outcomes (JSONB) ─────────────────────────────
	skills_gained = Column(JSONB, default=list, nullable=False)
	syllabus = Column(JSONB, default=list, nullable=False)

	# ── Media & display ───────────────────────────────────────
	images = Column(JSONB, default=list, nullable=False)
	visible = Column(Boolean, default=True, nullable=False, index=True)
	order = Column(Integer, default=0, nullable=False, index=True)

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

