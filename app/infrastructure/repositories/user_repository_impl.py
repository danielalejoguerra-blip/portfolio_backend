from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models.user_model import (
    PasswordResetCodeModel,
    RefreshTokenModel,
    UserModel,
)


class UserRepositoryImpl(UserRepository):
	def __init__(self, db: Session) -> None:
		self.db = db

	def get_by_email(self, email: str) -> Optional[User]:
		user = self.db.query(UserModel).filter(UserModel.email == email).first()
		if not user:
			return None
		return User(
			id=user.id,
			username=user.username,
			email=user.email,
			full_name=user.full_name,
			bio=user.bio,
			location=user.location,
			website=user.website,
			company=user.company,
			avatar_url=user.avatar_url,
			is_active=user.is_active,
		)

	def get_by_username(self, username: str) -> Optional[User]:
		user = self.db.query(UserModel).filter(UserModel.username == username).first()
		if not user:
			return None
		return User(
			id=user.id,
			username=user.username,
			email=user.email,
			full_name=user.full_name,
			bio=user.bio,
			location=user.location,
			website=user.website,
			company=user.company,
			avatar_url=user.avatar_url,
			is_active=user.is_active,
		)

	def get_by_id(self, user_id: int) -> Optional[User]:
		user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
		if not user:
			return None
		return User(
			id=user.id,
			username=user.username,
			email=user.email,
			full_name=user.full_name,
			bio=user.bio,
			location=user.location,
			website=user.website,
			company=user.company,
			avatar_url=user.avatar_url,
			is_active=user.is_active,
		)

	def create_user(
		self,
		username: str,
		email: str,
		hashed_password: str,
		full_name: Optional[str] = None,
		bio: Optional[str] = None,
		location: Optional[str] = None,
		website: Optional[str] = None,
		company: Optional[str] = None,
		avatar_url: Optional[str] = None,
	) -> User:
		db_user = UserModel(
			username=username,
			email=email,
			hashed_password=hashed_password,
			full_name=full_name,
			bio=bio,
			location=location,
			website=website,
			company=company,
			avatar_url=avatar_url,
		)
		self.db.add(db_user)
		self.db.commit()
		self.db.refresh(db_user)
		return User(
			id=db_user.id,
			username=db_user.username,
			email=db_user.email,
			full_name=db_user.full_name,
			bio=db_user.bio,
			location=db_user.location,
			website=db_user.website,
			company=db_user.company,
			avatar_url=db_user.avatar_url,
			is_active=db_user.is_active,
		)

	def get_password_hash(self, email: str) -> Optional[str]:
		user = self.db.query(UserModel).filter(UserModel.email == email).first()
		if not user:
			return None
		return user.hashed_password

	def add_refresh_token(self, user_id: int, token_hash: str, jti: str, expires_at: datetime) -> None:
		token = RefreshTokenModel(
			user_id=user_id,
			token_hash=token_hash,
			jti=jti,
			expires_at=expires_at,
			revoked=False,
		)
		self.db.add(token)
		self.db.commit()

	def get_refresh_token(self, token_hash: str) -> Optional[dict]:
		token = (
			self.db.query(RefreshTokenModel)
			.filter(RefreshTokenModel.token_hash == token_hash)
			.first()
		)
		if not token:
			return None
		return {
			"id": token.id,
			"user_id": token.user_id,
			"token_hash": token.token_hash,
			"jti": token.jti,
			"revoked": token.revoked,
			"expires_at": token.expires_at,
		}

	def revoke_refresh_token(self, token_hash: str) -> None:
		token = (
			self.db.query(RefreshTokenModel)
			.filter(RefreshTokenModel.token_hash == token_hash)
			.first()
		)
		if not token:
			return None
		token.revoked = True
		self.db.add(token)
		self.db.commit()

	def update_user(
		self,
		user_id: int,
		full_name: Optional[str] = None,
		bio: Optional[str] = None,
		location: Optional[str] = None,
		website: Optional[str] = None,
		company: Optional[str] = None,
		avatar_url: Optional[str] = None,
	) -> Optional[User]:
		user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
		if not user:
			return None

		# Solo actualizar los campos que no son None
		if full_name is not None:
			user.full_name = full_name
		if bio is not None:
			user.bio = bio
		if location is not None:
			user.location = location
		if website is not None:
			user.website = website
		if company is not None:
			user.company = company
		if avatar_url is not None:
			user.avatar_url = avatar_url

		self.db.commit()
		self.db.refresh(user)

		return User(
			id=user.id,
			username=user.username,
			email=user.email,
			full_name=user.full_name,
			bio=user.bio,
			location=user.location,
			website=user.website,
			company=user.company,
			avatar_url=user.avatar_url,
			is_active=user.is_active,
		)

	# ------------------------------------------------------------------ #
	#  Password reset                                                       #
	# ------------------------------------------------------------------ #

	def create_password_reset_code(
		self, user_id: int, code_hash: str, expires_at: datetime
	) -> None:
		record = PasswordResetCodeModel(
			user_id=user_id,
			code_hash=code_hash,
			expires_at=expires_at,
			used=False,
		)
		self.db.add(record)
		self.db.commit()

	def get_valid_reset_code(self, user_id: int) -> Optional[dict]:
		record = (
			self.db.query(PasswordResetCodeModel)
			.filter(
				PasswordResetCodeModel.user_id == user_id,
				PasswordResetCodeModel.used.is_(False),
			)
			.order_by(PasswordResetCodeModel.created_at.desc())
			.first()
		)
		if not record:
			return None
		return {
			"id": record.id,
			"user_id": record.user_id,
			"code_hash": record.code_hash,
			"expires_at": record.expires_at,
		}

	def mark_reset_code_used(self, code_id: int) -> None:
		record = self.db.query(PasswordResetCodeModel).filter(
			PasswordResetCodeModel.id == code_id
		).first()
		if record:
			record.used = True
			self.db.commit()

	def invalidate_user_reset_codes(self, user_id: int) -> None:
		self.db.query(PasswordResetCodeModel).filter(
			PasswordResetCodeModel.user_id == user_id,
			PasswordResetCodeModel.used.is_(False),
		).update({"used": True})
		self.db.commit()

	def update_password(self, user_id: int, hashed_password: str) -> None:
		user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
		if user:
			user.hashed_password = hashed_password
			self.db.commit()
