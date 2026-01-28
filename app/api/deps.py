from typing import Generator

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.services.user_service import UserService


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryImpl:
	return UserRepositoryImpl(db)


def get_user_service(repo: UserRepositoryImpl = Depends(get_user_repository)) -> UserService:
	return UserService(repo)


def get_current_user(
	request: Request,
	service: UserService = Depends(get_user_service),
):
	token = request.cookies.get(settings.COOKIE_ACCESS_NAME)
	if not token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
	try:
		payload = security.decode_token(token)
		if payload.get("type") != "access":
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
		user_id = int(payload.get("sub"))
	except (JWTError, ValueError, TypeError):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	user = service.get_user_by_id(user_id)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
	return user


def require_csrf(request: Request) -> None:
	csrf_cookie = request.cookies.get(settings.COOKIE_CSRF_NAME)
	csrf_header = request.headers.get(settings.CSRF_HEADER_NAME)
	if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token invalid")
