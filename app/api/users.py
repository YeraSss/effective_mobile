from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.services.auth import decode_token, is_token_revoked, revoke_token

router = APIRouter(prefix="/users", tags=["Пользователи"])

bearer_scheme = HTTPBearer()


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Получить профиль текущего пользователя."""
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновить данные профиля текущего пользователя."""
    if data.first_name is not None:
        current_user.first_name = data.first_name.strip()
    if data.last_name is not None:
        current_user.last_name = data.last_name.strip()
    if data.middle_name is not None:
        current_user.middle_name = data.middle_name.strip()

    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Мягкое удаление аккаунта: is_active=False + logout.
    Пользователь больше не сможет залогиниться, но запись в БД сохраняется.
    """
    current_user.is_active = False
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()

    # Отзываем текущий токен
    payload = decode_token(credentials.credentials)
    if payload:
        jti = payload.get("jti")
        if jti and not is_token_revoked(jti, db):
            revoke_token(jti, db)

    return {"detail": "Аккаунт деактивирован. До свидания!"}
