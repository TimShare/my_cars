from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from core.entites.car import FuelType, TransmissionType, DriveType, CarCondition


class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    country: Optional[str] = None
    logo_url: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BrandBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class BrandResponse(BrandBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    brand_id: UUID
    year_from: Optional[int] = None
    year_to: Optional[int] = None


class ModelCreate(ModelBase):
    @field_validator("year_from", "year_to")
    def validate_year(cls, v):
        if v is not None and (v < 1900 or v > datetime.now().year + 5):
            raise ValueError(f"Год должен быть между 1900 и {datetime.now().year + 5}")
        return v


class ModelUpdate(ModelBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand_id: Optional[UUID] = None

    @field_validator("year_from", "year_to")
    def validate_year(cls, v):
        if v is not None and (v < 1900 or v > datetime.now().year + 5):
            raise ValueError(f"Год должен быть между 1900 и {datetime.now().year + 5}")
        return v


class ModelResponse(ModelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CarBase(BaseModel):
    model_id: UUID
    year: int = Field(..., ge=1900, le=datetime.now().year + 5)
    price: float = Field(..., ge=0)
    mileage: int = Field(..., ge=0)
    condition: CarCondition
    fuel_type: FuelType
    transmission: TransmissionType
    drive_type: DriveType
    seller_id: Optional[UUID] = None
    color: Optional[str] = None
    engine_volume: Optional[float] = Field(None, ge=0, le=20)
    power: Optional[int] = Field(None, ge=0, le=2000)
    description: Optional[str] = None
    vin: Optional[str] = Field(None, min_length=10, max_length=17)
    is_sold: bool = False
    photos: List[str] = []


class CarCreate(CarBase):
    pass


class CarUpdate(CarBase):
    model_id: Optional[UUID] = None
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 5)
    price: Optional[float] = Field(None, ge=0)
    mileage: Optional[int] = Field(None, ge=0)
    condition: Optional[CarCondition] = None
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    drive_type: Optional[DriveType] = None


class CarResponse(CarBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CarDetailResponse(CarResponse):
    brand: BrandResponse
    model: ModelResponse

    class Config:
        from_attributes = True
