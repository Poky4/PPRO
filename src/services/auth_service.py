from typing import Optional
from sqlalchemy.orm import Session
from src.domain.models.user import User
from src.core.security import verify_password
from src.services.user_service import UserService


class AuthService:
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        user = UserService.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
