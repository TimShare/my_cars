from datetime import datetime
from typing import List
from uuid import UUID
from sqlalchemy import ARRAY, ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from infrastructure.models.base import BaseModelMixin
from infrastructure.postgres_db import Base


class BannedRefreshToken(Base, BaseModelMixin):
    __tablename__ = "BannedRefreshTokens"

    jti: Mapped[str] = mapped_column(nullable=False, unique=True)



class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    surname: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    scopes: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])


