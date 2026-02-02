"""
Analytics event ORM model for database persistence.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.session import Base


class AnalyticsEventModel(Base):
	__tablename__ = "analytics_events"

	id = Column(Integer, primary_key=True, index=True)
	event_type = Column(String(50), nullable=False, index=True)
	page_slug = Column(String(255), nullable=True, index=True)
	content_type = Column(String(50), nullable=True, index=True)
	content_id = Column(Integer, nullable=True, index=True)
	referrer = Column(String(2000), nullable=True)
	user_agent = Column(Text, nullable=True)
	ip_hash = Column(String(64), nullable=True, index=True)  # SHA-256 hash
	country = Column(String(2), nullable=True, index=True)  # ISO 3166-1 alpha-2
	meta = Column("metadata", JSONB, default=dict, nullable=False)
	created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
