from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_user_service, require_csrf
from app.domain.schemas.user import UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user=Depends(get_current_user)):
	return current_user


@router.put("/me", response_model=UserRead, dependencies=[Depends(require_csrf)])
def update_current_user(
	payload: UserUpdate,
	current_user=Depends(get_current_user),
	service: UserService = Depends(get_user_service),
):
	updated_user = service.update_user(
		user_id=current_user.id,
		full_name=payload.full_name,
		bio=payload.bio,
		location=payload.location,
		website=payload.website,
		company=payload.company,
		avatar_url=payload.avatar_url,
	)
	if not updated_user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
	return updated_user
