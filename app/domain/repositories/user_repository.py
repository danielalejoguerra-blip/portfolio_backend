from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.domain.entities.user import User


class UserRepository(ABC):
	@abstractmethod
	def get_by_email(self, email: str) -> Optional[User]:
		raise NotImplementedError()

	@abstractmethod
	def get_by_username(self, username: str) -> Optional[User]:
		raise NotImplementedError()

	@abstractmethod
	def get_by_id(self, user_id: int) -> Optional[User]:
		raise NotImplementedError()

	@abstractmethod
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
		raise NotImplementedError()

	@abstractmethod
	def get_password_hash(self, email: str) -> Optional[str]:
		raise NotImplementedError()

	@abstractmethod
	def add_refresh_token(self, user_id: int, token_hash: str, jti: str, expires_at: datetime) -> None:
		raise NotImplementedError()

	@abstractmethod
	def get_refresh_token(self, token_hash: str) -> Optional[dict]:
		raise NotImplementedError()

	@abstractmethod
	def revoke_refresh_token(self, token_hash: str) -> None:
		raise NotImplementedError()

	@abstractmethod
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
		raise NotImplementedError()
