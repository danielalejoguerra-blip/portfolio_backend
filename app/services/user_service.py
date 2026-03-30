from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError

from app.core import security
from app.core.config import settings
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class UserService:
	def __init__(self, repository: UserRepository) -> None:
		self.repository = repository

	def register_user(
		self,
		username: str,
		email: str,
		password: str,
		full_name: Optional[str] = None,
		bio: Optional[str] = None,
		location: Optional[str] = None,
		website: Optional[str] = None,
		company: Optional[str] = None,
		avatar_url: Optional[str] = None,
	) -> User:
		# Verificar si el email ya existe
		existing = self.repository.get_by_email(email)
		if existing:
			raise ValueError("email_already_registered")
		
		# Verificar si el username ya existe
		existing_username = self.repository.get_by_username(username)
		if existing_username:
			raise ValueError("username_already_taken")
		
		hashed = security.hash_password(password)
		return self.repository.create_user(
			username=username,
			email=email,
			hashed_password=hashed,
			full_name=full_name,
			bio=bio,
			location=location,
			website=website,
			company=company,
			avatar_url=avatar_url,
		)

	def authenticate_user(self, email: str, password: str) -> Optional[User]:
		user = self.repository.get_by_email(email)
		if not user:
			return None
		hashed = self.repository.get_password_hash(email)
		if not hashed or not security.verify_password(password, hashed):
			return None
		return user

	def create_login_tokens(self, user_id: int) -> dict:
		access_token = security.create_access_token(subject=str(user_id))
		refresh_token, refresh_exp, refresh_jti = security.create_refresh_token(subject=str(user_id))
		refresh_hash = security.hash_token(refresh_token)
		self.repository.add_refresh_token(user_id, refresh_hash, refresh_jti, refresh_exp)
		csrf_token = security.create_csrf_token()
		return {
			"access_token": access_token,
			"refresh_token": refresh_token,
			"refresh_expires": refresh_exp,
			"csrf_token": csrf_token,
		}

	def refresh_login_tokens(self, refresh_token: str) -> dict:
		token_hash = security.hash_token(refresh_token)
		stored = self.repository.get_refresh_token(token_hash)
		if not stored or stored["revoked"]:
			raise ValueError("invalid_refresh_token")
		if stored["expires_at"] < datetime.now(timezone.utc):
			raise ValueError("refresh_expired")

		try:
			payload = security.decode_token(refresh_token)
		except JWTError:
			raise ValueError("invalid_refresh_token")
		if payload.get("type") != "refresh":
			raise ValueError("invalid_refresh_token")

		self.repository.revoke_refresh_token(token_hash)

		user_id = int(payload.get("sub"))
		access_token = security.create_access_token(subject=str(user_id))
		new_refresh_token, refresh_exp, refresh_jti = security.create_refresh_token(subject=str(user_id))
		new_refresh_hash = security.hash_token(new_refresh_token)
		self.repository.add_refresh_token(user_id, new_refresh_hash, refresh_jti, refresh_exp)
		csrf_token = security.create_csrf_token()

		return {
			"access_token": access_token,
			"refresh_token": new_refresh_token,
			"refresh_expires": refresh_exp,
			"csrf_token": csrf_token,
		}

	def logout(self, refresh_token: str) -> None:
		token_hash = security.hash_token(refresh_token)
		self.repository.revoke_refresh_token(token_hash)

	def get_user_by_id(self, user_id: int) -> Optional[User]:
		return self.repository.get_by_id(user_id)

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
		return self.repository.update_user(
			user_id=user_id,
			full_name=full_name,
			bio=bio,
			location=location,
			website=website,
			company=company,
			avatar_url=avatar_url,
		)

	# ------------------------------------------------------------------ #
	#  Password reset                                                       #
	# ------------------------------------------------------------------ #

	def request_password_reset(self, email: str, email_service) -> None:
		"""Genera un código OTP, lo almacena y envía el email.
		Siempre retorna sin error para no filtrar la existencia del usuario.
		"""
		user = self.repository.get_by_email(email)
		if not user:
			return

		# Invalida cualquier código pendiente anterior
		self.repository.invalidate_user_reset_codes(user.id)

		code = security.generate_reset_code()
		code_hash = security.hash_reset_code(code)
		expires_at = datetime.now(timezone.utc) + timedelta(
			minutes=settings.PASSWORD_RESET_CODE_EXPIRE_MINUTES
		)
		self.repository.create_password_reset_code(user.id, code_hash, expires_at)
		email_service.send_password_reset_email(user.email, code, user.username or user.email)

	def confirm_password_reset(self, email: str, code: str, new_password: str) -> None:
		"""Verifica el código OTP y actualiza la contraseña."""
		user = self.repository.get_by_email(email)
		if not user:
			raise ValueError("invalid_reset_code")

		stored = self.repository.get_valid_reset_code(user.id)
		if not stored:
			raise ValueError("invalid_reset_code")

		if stored["expires_at"] < datetime.now(timezone.utc):
			self.repository.mark_reset_code_used(stored["id"])
			raise ValueError("reset_code_expired")

		code_hash = security.hash_reset_code(code)
		if not security.safe_compare(code_hash, stored["code_hash"]):
			raise ValueError("invalid_reset_code")

		self.repository.mark_reset_code_used(stored["id"])
		new_hashed = security.hash_password(new_password)
		self.repository.update_password(user.id, new_hashed)
