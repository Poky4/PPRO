from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_current_active_user, require_admin
from src.domain.models.user import User, UserRole
from src.schemas.user import UserCreate, UserResponse, UserUpdate
from src.services.user_service import UserService

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserResponse],
    dependencies=[Depends(require_admin)],
    summary="Seznam uživatelů (pouze ADMIN)",
)
def read_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Počet přeskočených záznamů"),
    limit: int = Query(100, ge=1, le=200, description="Maximální počet záznamů"),
    role: Optional[UserRole] = Query(None, description="Filtrovat dle role"),
) -> List[User]:
    """Vrátí seznam uživatelů se stránkováním a volitelnou filtrací dle role."""
    return UserService.get_multi(db, skip=skip, limit=limit, role=role)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
    summary="Vytvoření nového uživatele (pouze ADMIN)",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """Založí nového uživatele se zadanou rolí a heslem."""
    return UserService.create(db, user_in)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Detail uživatele (ADMIN nebo vlastník účtu)",
)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Zobrazí detail uživatele dle ID."""
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění prohlížet profil jiného uživatele.",
        )
    user = UserService.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uživatel s ID {user_id} nebyl nalezen.",
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
    summary="Úprava uživatele (pouze ADMIN)",
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
) -> User:
    """Upraví údaje existujícího uživatele."""
    user = UserService.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uživatel s ID {user_id} nebyl nalezen.",
        )
    return UserService.update(db, db_obj=user, obj_in=user_in)


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
    summary="Deaktivace uživatele (pouze ADMIN)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Deaktivuje uživatelský účet (soft delete). Zabraňuje smazání vlastního účtu admina."""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrátor nemůže deaktivovat svůj vlastní běžící účet.",
        )
    user = UserService.delete(db, user_id=user_id, soft=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uživatel s ID {user_id} nebyl nalezen.",
        )
    return user
