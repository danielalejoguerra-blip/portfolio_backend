from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
	now = datetime.now(timezone.utc)
	expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode = {
		"sub": subject,
		"type": "access",
		"jti": str(uuid.uuid4()),
		"iat": int(now.timestamp()),
		"exp": expire,
	}
	return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> tuple[str, datetime, str]:
	now = datetime.now(timezone.utc)
	expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
	jti = str(uuid.uuid4())
	to_encode = {
		"sub": subject,
		"type": "refresh",
		"jti": jti,
		"iat": int(now.timestamp()),
		"exp": expire,
	}
	token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
	return token, expire, jti


def decode_token(token: str) -> dict:
	return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def hash_token(token: str) -> str:
	return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_csrf_token() -> str:
	return secrets.token_urlsafe(32)
