from typing import Generator, Optional

from fastapi import Depends, Header, HTTPException, Query, Request, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.repositories.project_repository_impl import ProjectRepositoryImpl
from app.infrastructure.repositories.blog_repository_impl import BlogRepositoryImpl
from app.infrastructure.repositories.course_repository_impl import CourseRepositoryImpl
from app.infrastructure.repositories.education_repository_impl import EducationRepositoryImpl
from app.infrastructure.repositories.experience_repository_impl import ExperienceRepositoryImpl
from app.infrastructure.repositories.analytics_repository_impl import AnalyticsRepositoryImpl
from app.infrastructure.repositories.personal_info_repository_impl import PersonalInfoRepositoryImpl
from app.infrastructure.repositories.skill_repository_impl import SkillRepositoryImpl
from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.blog_service import BlogService
from app.services.course_service import CourseService
from app.services.education_service import EducationService
from app.services.experience_service import ExperienceService
from app.services.analytics_service import AnalyticsService
from app.services.personal_info_service import PersonalInfoService
from app.services.skill_service import SkillService
from app.services.email_service import EmailService
from app.services.ai_translation_service import AITranslationService


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


def get_email_service() -> EmailService:
	return EmailService()


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
	print(f"[CSRF DEBUG] cookie_name={settings.COOKIE_CSRF_NAME} header_name={settings.CSRF_HEADER_NAME}")
	print(f"[CSRF DEBUG] cookie={csrf_cookie!r}")
	print(f"[CSRF DEBUG] header={csrf_header!r}")
	print(f"[CSRF DEBUG] all_cookies={dict(request.cookies)}")
	if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token invalid")


def get_language(
	lang: Optional[str] = Query(None, description="Language code (es, en)"),
	accept_language: Optional[str] = Header(None),
) -> str:
	"""Resolve the requested language from query param or Accept-Language header."""
	if lang and lang in SUPPORTED_LANGUAGES:
		return lang
	if accept_language:
		for part in accept_language.split(","):
			code = part.strip().split(";")[0].strip().lower()[:2]
			if code in SUPPORTED_LANGUAGES:
				return code
	return DEFAULT_LANGUAGE


# ============================================================================
# AI Translation
# ============================================================================

def get_ai_translation_service() -> AITranslationService:
	return AITranslationService()


# ============================================================================
# Content Domain Dependencies
# ============================================================================

# Project dependencies
def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepositoryImpl:
	return ProjectRepositoryImpl(db)


def get_project_service(
	repo: ProjectRepositoryImpl = Depends(get_project_repository),
	ai_translator: AITranslationService = Depends(get_ai_translation_service),
) -> ProjectService:
	return ProjectService(repo, ai_translator)


# Blog dependencies
def get_blog_repository(db: Session = Depends(get_db)) -> BlogRepositoryImpl:
	return BlogRepositoryImpl(db)


def get_blog_service(
	repo: BlogRepositoryImpl = Depends(get_blog_repository),
	ai_translator: AITranslationService = Depends(get_ai_translation_service),
) -> BlogService:
	return BlogService(repo, ai_translator)


# Course dependencies
def get_course_repository(db: Session = Depends(get_db)) -> CourseRepositoryImpl:
	return CourseRepositoryImpl(db)


def get_course_service(
	repo: CourseRepositoryImpl = Depends(get_course_repository),
	ai_translator: AITranslationService = Depends(get_ai_translation_service),
) -> CourseService:
	return CourseService(repo, ai_translator)


# Education dependencies
def get_education_repository(db: Session = Depends(get_db)) -> EducationRepositoryImpl:
	return EducationRepositoryImpl(db)


def get_education_service(
	repo: EducationRepositoryImpl = Depends(get_education_repository),
	ai_translator: AITranslationService = Depends(get_ai_translation_service),
) -> EducationService:
	return EducationService(repo, ai_translator)


# Experience dependencies
def get_experience_repository(db: Session = Depends(get_db)) -> ExperienceRepositoryImpl:
	return ExperienceRepositoryImpl(db)


def get_experience_service(
	repo: ExperienceRepositoryImpl = Depends(get_experience_repository),
	ai_translator: AITranslationService = Depends(get_ai_translation_service),
) -> ExperienceService:
	return ExperienceService(repo, ai_translator)


# Analytics dependencies
def get_analytics_repository(db: Session = Depends(get_db)) -> AnalyticsRepositoryImpl:
	return AnalyticsRepositoryImpl(db)


def get_analytics_service(repo: AnalyticsRepositoryImpl = Depends(get_analytics_repository)) -> AnalyticsService:
	return AnalyticsService(repo)


# Personal info dependencies
def get_personal_info_repository(db: Session = Depends(get_db)) -> PersonalInfoRepositoryImpl:
	return PersonalInfoRepositoryImpl(db)


def get_personal_info_service(
	repo: PersonalInfoRepositoryImpl = Depends(get_personal_info_repository),
	ai_translator: AITranslationService = Depends(get_ai_translation_service),
) -> PersonalInfoService:
	return PersonalInfoService(repo, ai_translator)


# Skill dependencies
def get_skill_repository(db: Session = Depends(get_db)) -> SkillRepositoryImpl:
	return SkillRepositoryImpl(db)


def get_skill_service(
	repo: SkillRepositoryImpl = Depends(get_skill_repository),
	ai_translator: AITranslationService = Depends(get_ai_translation_service),
) -> SkillService:
	return SkillService(repo, ai_translator)
