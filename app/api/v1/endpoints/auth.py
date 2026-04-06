from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status

from app.api.deps import get_current_user, get_email_service, get_user_service, require_csrf
from app.core import security
from app.core.config import settings
from app.domain.schemas.user import PasswordResetConfirm, PasswordResetRequest, UserCreate, UserLogin, UserRead
from app.services.email_service import EmailService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str) -> None:
	response.set_cookie(
		key=settings.COOKIE_ACCESS_NAME,
		value=access_token,
		httponly=True,
		secure=settings.COOKIE_SECURE,
		samesite=settings.COOKIE_SAMESITE,
		domain=settings.COOKIE_DOMAIN,
		path=settings.COOKIE_PATH,
		max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
	)
	response.set_cookie(
		key=settings.COOKIE_REFRESH_NAME,
		value=refresh_token,
		httponly=True,
		secure=settings.COOKIE_SECURE,
		samesite=settings.COOKIE_SAMESITE,
		domain=settings.COOKIE_DOMAIN,
		path=settings.COOKIE_PATH,
		max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
	)
	response.set_cookie(
		key=settings.COOKIE_CSRF_NAME,
		value=csrf_token,
		httponly=False,
		secure=settings.COOKIE_SECURE,
		samesite=settings.COOKIE_SAMESITE,
		domain=settings.COOKIE_DOMAIN,
		path=settings.COOKIE_PATH,
		max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
	)


def _clear_auth_cookies(response: Response) -> None:
	response.delete_cookie(key=settings.COOKIE_ACCESS_NAME, domain=settings.COOKIE_DOMAIN, path=settings.COOKIE_PATH)
	response.delete_cookie(key=settings.COOKIE_REFRESH_NAME, domain=settings.COOKIE_DOMAIN, path=settings.COOKIE_PATH)
	response.delete_cookie(key=settings.COOKIE_CSRF_NAME, domain=settings.COOKIE_DOMAIN, path=settings.COOKIE_PATH)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def register_user(payload: UserCreate, service: UserService = Depends(get_user_service)):
	try:
		user = service.register_user(
			username=payload.username,
			email=payload.email,
			password=payload.password,
			full_name=payload.full_name,
			bio=payload.bio,
			location=payload.location,
			website=payload.website,
			company=payload.company,
			avatar_url=payload.avatar_url,
		)
		return user
	except ValueError as e:
		error_msg = str(e)
		if "email" in error_msg:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
		elif "username" in error_msg:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=UserRead)
def login_user(
	payload: UserLogin,
	response: Response,
	service: UserService = Depends(get_user_service),
):
	print("[login] email:", payload.email)
	print("[login] password_length:", payload.password)
	user = service.authenticate_user(payload.email, payload.password)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	tokens = service.create_login_tokens(user.id)
	_set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"], tokens["csrf_token"])
	return user


@router.post("/refresh", response_model=UserRead, dependencies=[Depends(require_csrf)])
def refresh_tokens(
	request: Request,
	response: Response,
	service: UserService = Depends(get_user_service),
):
	refresh_token = request.cookies.get(settings.COOKIE_REFRESH_NAME)
	if refresh_token is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

	try:
		tokens = service.refresh_login_tokens(refresh_token)
	except ValueError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
	_set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"], tokens["csrf_token"])
	user_id = int(security.decode_token(tokens["access_token"]).get("sub"))
	user = service.get_user_by_id(user_id)
	return user


@router.post("/logout", dependencies=[Depends(require_csrf)])
def logout_user(
	request: Request,
	response: Response,
	service: UserService = Depends(get_user_service),
):
	refresh_token = request.cookies.get(settings.COOKIE_REFRESH_NAME)
	if refresh_token:
		service.logout(refresh_token)
	_clear_auth_cookies(response)
	return {"status": "ok"}


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(
	payload: PasswordResetRequest,
	background_tasks: BackgroundTasks,
	service: UserService = Depends(get_user_service),
	email_service: EmailService = Depends(get_email_service),
):
	"""Solicita un código OTP de 6 dígitos al email indicado.
	Siempre responde 202 para no filtrar la existencia del usuario.
	"""
	background_tasks.add_task(
		service.request_password_reset,
		email=payload.email,
		email_service=email_service,
	)
	return {"detail": "Si el email existe, recibirás un código de verificación."}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
def confirm_password_reset(
	payload: PasswordResetConfirm,
	service: UserService = Depends(get_user_service),
):
	"""Verifica el código OTP y establece la nueva contraseña."""
	try:
		service.confirm_password_reset(
			email=payload.email,
			code=payload.code,
			new_password=payload.new_password,
		)
	except ValueError as exc:
		error = str(exc)
		if error == "reset_code_expired":
			raise HTTPException(
				status_code=status.HTTP_410_GONE,
				detail="El código de verificación ha expirado.",
			)
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Código de verificación inválido.",
		)
	return {"detail": "Contraseña actualizada correctamente."}
