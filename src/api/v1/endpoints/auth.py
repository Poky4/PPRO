from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_current_active_user
from src.core.security import create_access_token
from src.domain.models.user import User
from src.schemas.auth import Token
from src.schemas.user import UserResponse
from src.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=Token, summary="Přihlášení a získání JWT tokenu")
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """Přihlásí uživatele a vrátí JWT access token (kompatibilní se Swagger Authorize)."""
    user = AuthService.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nesprávné přihlašovací jméno nebo heslo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uživatelský účet je deaktivován.",
        )

    access_token = create_access_token(subject=user.username)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse, summary="Profil aktuálně přihlášeného uživatele")
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Vrátí profil přihlášeného uživatele identifikovaného z JWT Bearer tokenu."""
    return current_user
