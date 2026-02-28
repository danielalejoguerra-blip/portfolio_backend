"""
Personal information Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class PersonalInfoCreate(BaseModel):
	"""Schema for creating a personal info entry"""
	full_name: str = Field(min_length=1, max_length=255)
	headline: Optional[str] = Field(None, max_length=255)
	bio: Optional[str] = None
	email: Optional[EmailStr] = None
	phone: Optional[str] = Field(None, max_length=50)
	location: Optional[str] = Field(None, max_length=255)
	website: Optional[HttpUrl] = None
	avatar_url: Optional[HttpUrl] = None
	resume_url: Optional[HttpUrl] = None
	social_links: dict[str, str] = Field(default_factory=dict)
	metadata: dict = Field(default_factory=dict)
	visible: bool = True
	order: int = Field(default=0, ge=0)


class PersonalInfoUpdate(BaseModel):
	"""Schema for updating a personal info entry"""
	full_name: Optional[str] = Field(None, min_length=1, max_length=255)
	headline: Optional[str] = Field(None, max_length=255)
	bio: Optional[str] = None
	email: Optional[EmailStr] = None
	phone: Optional[str] = Field(None, max_length=50)
	location: Optional[str] = Field(None, max_length=255)
	website: Optional[HttpUrl] = None
	avatar_url: Optional[HttpUrl] = None
	resume_url: Optional[HttpUrl] = None
	social_links: Optional[dict[str, str]] = None
	metadata: Optional[dict] = None
	visible: Optional[bool] = None
	order: Optional[int] = Field(None, ge=0)


class PersonalInfoRead(BaseModel):
	"""Schema for personal info response"""
	id: int
	full_name: str
	headline: Optional[str] = None
	bio: Optional[str] = None
	email: Optional[EmailStr] = None
	phone: Optional[str] = None
	location: Optional[str] = None
	website: Optional[HttpUrl] = None
	avatar_url: Optional[HttpUrl] = None
	resume_url: Optional[HttpUrl] = None
	social_links: dict[str, str] = Field(default_factory=dict)
	metadata: dict = Field(default_factory=dict)
	visible: bool
	order: int
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None

	class Config:
		from_attributes = True


class PersonalInfoListResponse(BaseModel):
	"""Paginated personal info list response"""
	items: list[PersonalInfoRead]
	total: int
	limit: int
	offset: int
	has_more: bool
