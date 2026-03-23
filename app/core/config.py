from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=".env",
		env_ignore_empty=True,
		extra="ignore",
	)

	PROJECT_NAME: str = "Portfolio API"
	API_V1_STR: str = "/api/v1"

	DATABASE_URL: str = "sqlite:///./test.db"

	ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
	REFRESH_TOKEN_EXPIRE_DAYS: int = 14

	JWT_SECRET_KEY: str = "CHANGE_ME"
	JWT_ALGORITHM: str = "HS256"

	COOKIE_ACCESS_NAME: str = "access_token"
	COOKIE_REFRESH_NAME: str = "refresh_token"
	COOKIE_CSRF_NAME: str = "csrf_token"
	COOKIE_DOMAIN: Optional[str] = None
	COOKIE_PATH: str = "/"
	COOKIE_SECURE: bool = True
	COOKIE_SAMESITE: str = "lax"

	CSRF_HEADER_NAME: str = "X-CSRF-Token"

	BACKEND_CORS_ORIGINS: List[str] = []

	SOCKETIO_PATH: str = "socket.io"
	SOCKETIO_NAMESPACE_ANALYTICS: str = "/analytics"
	SOCKETIO_ANALYTICS_ROOM: str = "analytics_admin"
	SOCKETIO_REDIS_URL: Optional[str] = None

	ANALYTICS_REALTIME_DAYS: int = 30
	ANALYTICS_REALTIME_TOP_LIMIT: int = 10

	GMAIL_SENDER_EMAIL: Optional[str] = None
	GMAIL_APP_PASSWORD: Optional[str] = None
	PASSWORD_RESET_CODE_EXPIRE_MINUTES: int = 15

	GEMINI_API_KEY: Optional[str] = None


settings = Settings()
