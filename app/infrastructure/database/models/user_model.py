from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.infrastructure.database.session import Base


class UserModel(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String(50), unique=True, index=True, nullable=False)
	email = Column(String(255), unique=True, index=True, nullable=False)
	full_name = Column(String(255), nullable=True)
	bio = Column(Text, nullable=True)
	location = Column(String(255), nullable=True)
	website = Column(String(500), nullable=True)
	company = Column(String(255), nullable=True)
	avatar_url = Column(String(500), nullable=True)
	hashed_password = Column(Text, nullable=False)
	is_active = Column(Boolean, default=True, nullable=False)
	created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
	updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

	refresh_tokens = relationship("RefreshTokenModel", back_populates="user")


class RefreshTokenModel(Base):
	__tablename__ = "refresh_tokens"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
	token_hash = Column(String(128), nullable=False, index=True)
	jti = Column(String(36), nullable=False, index=True)
	revoked = Column(Boolean, default=False, nullable=False)
	expires_at = Column(DateTime(timezone=True), nullable=False)
	created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

	user = relationship("UserModel", back_populates="refresh_tokens")
