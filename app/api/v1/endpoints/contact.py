import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from app.api.deps import get_email_service
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["Contact"])

# Simple in-memory rate limit: max 3 emails per IP every 60 seconds
_rate_limit: dict[str, list[float]] = {}
_RATE_LIMIT_MAX = 3
_RATE_LIMIT_WINDOW = 60  # seconds


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=2000)


class ContactResponse(BaseModel):
    success: bool
    message: str


def _check_rate_limit(client_ip: str) -> None:
    now = time.time()
    timestamps = _rate_limit.get(client_ip, [])
    # Keep only timestamps within the window
    timestamps = [t for t in timestamps if now - t < _RATE_LIMIT_WINDOW]
    if len(timestamps) >= _RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados mensajes enviados. Intenta de nuevo en unos minutos.",
        )
    timestamps.append(now)
    _rate_limit[client_ip] = timestamps


@router.post("", response_model=ContactResponse, status_code=status.HTTP_200_OK)
def send_contact_message(
    body: ContactRequest,
    request: Request,
    email_service: EmailService = Depends(get_email_service),
):
    """Public endpoint – sends a contact message to the portfolio owner."""
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    sent = email_service.send_contact_email(
        name=body.name,
        email=body.email,
        message=body.message,
    )

    if not sent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo enviar el mensaje en este momento. Intenta más tarde.",
        )

    return ContactResponse(
        success=True,
        message="Mensaje enviado correctamente. ¡Gracias por contactarme!",
    )
