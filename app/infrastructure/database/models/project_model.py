"""
Project ORM model for database persistence.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.session import Base


class ProjectModel(Base):
	__tablename__ = "projects"

	# ── Identity ───────────────────────────────────────────────
	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(255), nullable=False)
	slug = Column(String(255), unique=True, index=True, nullable=False)
	description = Column(String(1000), nullable=True)
	content = Column(Text, nullable=True)

	# ── Classification ───────────────────────────────────────
	status = Column(String(50), nullable=False, default="completed", index=True)
	category = Column(String(50), nullable=True, index=True)
	role = Column(String(255), nullable=True)

	# ── Timeline ─────────────────────────────────────────────
	start_date = Column(Date, nullable=True)
	end_date = Column(Date, nullable=True)

	# ── Collaboration ─────────────────────────────────────────
	team_size = Column(Integer, nullable=True)
	client = Column(String(255), nullable=True)

	# ── Tech stack (JSONB) ─────────────────────────────────────
	tech_stack = Column(JSONB, default=list, nullable=False)

	# ── Links ─────────────────────────────────────────────────
	project_url = Column(String(2048), nullable=True)
	repository_url = Column(String(2048), nullable=True)
	documentation_url = Column(String(2048), nullable=True)
	case_study_url = Column(String(2048), nullable=True)

	# ── Highlights (JSONB) ─────────────────────────────────────
	metrics = Column(JSONB, default=list, nullable=False)
	features = Column(JSONB, default=list, nullable=False)
	challenges = Column(JSONB, default=list, nullable=False)

	# ── Media & display ───────────────────────────────────────
	images = Column(JSONB, default=list, nullable=False)
	featured = Column(Boolean, default=False, nullable=False, index=True)
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

