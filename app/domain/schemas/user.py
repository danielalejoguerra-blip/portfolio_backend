from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
	username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
	email: EmailStr
	password: str = Field(min_length=8, max_length=128)
	full_name: Optional[str] = Field(None, max_length=255)
	bio: Optional[str] = None
	location: Optional[str] = Field(None, max_length=255)
	website: Optional[str] = Field(None, max_length=500)
	company: Optional[str] = Field(None, max_length=255)
	avatar_url: Optional[str] = Field(None, max_length=500)


class UserLogin(BaseModel):
	email: EmailStr
	password: str


class UserUpdate(BaseModel):
	full_name: Optional[str] = Field(None, max_length=255)
	bio: Optional[str] = None
	location: Optional[str] = Field(None, max_length=255)
	website: Optional[str] = Field(None, max_length=500)
	company: Optional[str] = Field(None, max_length=255)
	avatar_url: Optional[str] = Field(None, max_length=500)


class UserRead(BaseModel):
	id: int
	username: str
	email: EmailStr
	full_name: Optional[str] = None
	bio: Optional[str] = None
	location: Optional[str] = None
	website: Optional[str] = None
	company: Optional[str] = None
	avatar_url: Optional[str] = None
	is_active: bool

	class Config:
		from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(min_length=8, max_length=128)