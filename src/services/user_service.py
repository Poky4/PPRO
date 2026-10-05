from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.domain.models.user import User, UserRole
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
    ) -> List[User]:
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        return query.order_by(User.id).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, obj_in: UserCreate) -> User:
        # Check uniqueness of username
        existing_user = UserService.get_by_username(db, obj_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uživatel s přihlašovacím jménem '{obj_in.username}' již existuje.",
            )

        # Check uniqueness of email if provided
        if obj_in.email:
            existing_email = UserService.get_by_email(db, obj_in.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Uživatel s e-mailem '{obj_in.email}' již existuje.",
                )

        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role=obj_in.role,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        elif "password" in update_data:
            update_data.pop("password")

        if "email" in update_data and update_data["email"]:
            existing = UserService.get_by_email(db, update_data["email"])
            if existing and existing.id != db_obj.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"E-mail '{update_data['email']}' je již obsazen jiným uživatelem.",
                )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, user_id: int, soft: bool = True) -> Optional[User]:
        db_obj = UserService.get_by_id(db, user_id)
        if not db_obj:
            return None

        if soft:
            db_obj.is_active = False
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        else:
            db.delete(db_obj)
            db.commit()

        return db_obj
