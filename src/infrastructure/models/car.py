from datetime import datetime
from typing import List
from uuid import UUID
from sqlalchemy import ARRAY, ForeignKey, String, Float, Integer, Boolean, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from infrastructure.models.base import BaseModelMixin
from infrastructure.postgres_db import Base
from core.entites.car import FuelType, TransmissionType, DriveType, CarCondition


class Brand(Base, BaseModelMixin):
    __tablename__ = "brands"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    country: Mapped[str] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Отношение один-ко-многим: бренд имеет много моделей
    models: Mapped[List["Model"]] = relationship(back_populates="brand", cascade="all, delete-orphan")


class Model(Base, BaseModelMixin):
    __tablename__ = "models"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    year_from: Mapped[int] = mapped_column(Integer, nullable=True)
    year_to: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Отношения
    brand: Mapped["Brand"] = relationship(back_populates="models")
    cars: Mapped[List["Car"]] = relationship(back_populates="model", cascade="all, delete-orphan")


class Car(Base, BaseModelMixin):
    __tablename__ = "cars"
    
    model_id: Mapped[UUID] = mapped_column(ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    condition: Mapped[CarCondition] = mapped_column(Enum(CarCondition), nullable=False)
    fuel_type: Mapped[FuelType] = mapped_column(Enum(FuelType), nullable=False)
    transmission: Mapped[TransmissionType] = mapped_column(Enum(TransmissionType), nullable=False)
    drive_type: Mapped[DriveType] = mapped_column(Enum(DriveType), nullable=False)
    
    # Необязательные поля
    seller_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    color: Mapped[str] = mapped_column(String(50), nullable=True)
    engine_volume: Mapped[float] = mapped_column(Float, nullable=True)
    power: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)
    vin: Mapped[str] = mapped_column(String(17), nullable=True)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    photos: Mapped[List[str]] = mapped_column(ARRAY(String), default=[], nullable=False)
    
    # Отношения
    model: Mapped["Model"] = relationship(back_populates="cars")