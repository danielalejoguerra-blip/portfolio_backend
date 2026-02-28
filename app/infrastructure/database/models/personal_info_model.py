"""
Personal information ORM model for database persistence.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.session import Base


class PersonalInfoModel(Base):
	__tablename__ = "personal_info"

	id = Column(Integer, primary_key=True, index=True)
	full_name = Column(String(255), nullable=False)
	headline = Column(String(255), nullable=True)
	bio = Column(Text, nullable=True)
	email = Column(String(255), nullable=True)
	phone = Column(String(50), nullable=True)
	location = Column(String(255), nullable=True)
	website = Column(String(2048), nullable=True)
	avatar_url = Column(String(2048), nullable=True)
	resume_url = Column(String(2048), nullable=True)
	social_links = Column(JSONB, default=dict, nullable=False)
	meta = Column("metadata", JSONB, default=dict, nullable=False)
	visible = Column(Boolean, default=True, nullable=False, index=True)
	order = Column(Integer, default=0, nullable=False, index=True)
	created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
	deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
