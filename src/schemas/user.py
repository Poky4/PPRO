from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from src.domain.models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Přihlašovací jméno")
    email: Optional[EmailStr] = Field(None, description="Kontaktní e-mail")
    full_name: str = Field(..., min_length=1, max_length=100, description="Celé jméno uživatele")
    role: UserRole = Field(default=UserRole.RECEPCNI, description="Role v ordinaci")
    is_active: bool = Field(default=True, description="Příznak aktivního účtu")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Uživatelské heslo")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
