from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import List, Optional


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=3)
    surname: str = Field(..., min_length=3)
    scopes: List[str] = Field(default_factory=list)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    is_active: bool = True
    is_superuser: bool = False

    @field_validator("password")
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    scopes: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    blocked_at: Optional[datetime] = None


class UserResponse(UserBase):
    id: UUID
    email: EmailStr
    name: str
    surname: str
    scopes: List[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str
