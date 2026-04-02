"""
Experience ORM model for database persistence.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.session import Base


class ExperienceModel(Base):
	__tablename__ = "experiences"

	# ── Identity ───────────────────────────────────────────────
	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(255), nullable=False)
	slug = Column(String(255), unique=True, index=True, nullable=False)
	description = Column(String(1000), nullable=True)
	content = Column(Text, nullable=True)

	# ── Company ─────────────────────────────────────────────
	company = Column(String(255), nullable=False, index=True)
	company_url = Column(String(2048), nullable=True)
	company_logo_url = Column(String(2048), nullable=True)
	location = Column(String(255), nullable=True)

	# ── Role details ─────────────────────────────────────────
	employment_type = Column(String(20), nullable=False, default="full_time", index=True)
	work_mode = Column(String(10), nullable=True)
	department = Column(String(255), nullable=True)

	# ── Timeline ─────────────────────────────────────────────
	start_date = Column(Date, nullable=False, index=True)
	end_date = Column(Date, nullable=True)
	is_current = Column(Boolean, default=False, nullable=False, index=True)

	# ── Tech stack (JSONB) ─────────────────────────────────────
	tech_stack = Column(JSONB, default=list, nullable=False)

	# ── Highlights (JSONB) ─────────────────────────────────────
	responsibilities = Column(JSONB, default=list, nullable=False)
	achievements = Column(JSONB, default=list, nullable=False)
	related_projects = Column(JSONB, default=list, nullable=False)

	# ── References (JSONB) ─────────────────────────────────────
	references = Column(JSONB, default=list, nullable=False)

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

