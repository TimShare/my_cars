from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import List, Optional


class FuelType(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    GAS = "gas"


class TransmissionType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    ROBOT = "robot"
    VARIATOR = "variator"


class DriveType(str, Enum):
    FRONT = "front"
    REAR = "rear"
    FULL = "full"


class CarCondition(str, Enum):
    NEW = "new"
    USED = "used"


@dataclass
class Brand:
    """Бренд автомобиля"""

    name: str
    id: Optional[UUID] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Model:
    """Модель автомобиля"""

    name: str
    brand_id: UUID
    id: Optional[UUID] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Car:
    """Автомобиль"""

    model_id: UUID
    year: int
    price: float
    mileage: int
    condition: CarCondition
    fuel_type: FuelType
    transmission: TransmissionType
    drive_type: DriveType
    id: Optional[UUID] = None
    seller_id: Optional[UUID] = None
    color: Optional[str] = None
    engine_volume: Optional[float] = None
    power: Optional[int] = None
    description: Optional[str] = None
    vin: Optional[str] = None
    is_sold: bool = False
    photos: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
