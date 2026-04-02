"""
Education ORM model for database persistence.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.session import Base


class EducationModel(Base):
	__tablename__ = "education"

	# ── Identity ───────────────────────────────────────────────
	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(255), nullable=False)
	slug = Column(String(255), unique=True, index=True, nullable=False)
	description = Column(String(1000), nullable=True)
	content = Column(Text, nullable=True)

	# ── Institution ─────────────────────────────────────────
	institution = Column(String(255), nullable=False, index=True)
	institution_url = Column(String(2048), nullable=True)
	location = Column(String(255), nullable=True)

	# ── Programme ───────────────────────────────────────────
	degree_type = Column(String(50), nullable=False, default="bachelor", index=True)
	field_of_study = Column(String(255), nullable=True)
	start_date = Column(Date, nullable=True)
	end_date = Column(Date, nullable=True, index=True)

	# ── Credential ─────────────────────────────────────────
	credential_id = Column(String(255), nullable=True)
	credential_url = Column(String(2048), nullable=True)
	grade = Column(String(50), nullable=True)
	honors = Column(String(255), nullable=True)

	# ── Academic extras (JSONB lists) ───────────────────────────
	relevant_coursework = Column(JSONB, default=list, nullable=False)
	activities = Column(JSONB, default=list, nullable=False)
	achievements = Column(JSONB, default=list, nullable=False)

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

