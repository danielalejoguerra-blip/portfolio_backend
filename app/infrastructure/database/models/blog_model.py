"""
Blog post ORM model for database persistence.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.session import Base


class BlogPostModel(Base):
	__tablename__ = "blog_posts"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(255), nullable=False)
	slug = Column(String(255), unique=True, index=True, nullable=False)
	description = Column(String(1000), nullable=True)
	content = Column(Text, nullable=True)
	images = Column(JSONB, default=list, nullable=False)
	meta = Column("metadata", JSONB, default=dict, nullable=False)
	visible = Column(Boolean, default=True, nullable=False, index=True)
	published_at = Column(DateTime(timezone=True), nullable=True, index=True)
	created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
	deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
