from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.entites import Car as CarEntity
from core.entites import Brand as BrandEntity
from core.entites import Model as ModelEntity
from infrastructure.models import Car, Brand, Model
from core.InterfaceRepositories.ICar import (
    ICarRepository,
    IBrandRepository,
    IModelRepository,
)
from core.exceptions import NotFoundError


class BrandRepository(IBrandRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Brand) -> BrandEntity:
        return BrandEntity(
            id=model.id,
            name=model.name,
            country=model.country,
            logo_url=model.logo_url,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_all(self) -> List[BrandEntity]:
        stmt = select(Brand).order_by(Brand.name)
        result = await self.session.execute(stmt)
        return [self._to_entity(brand) for brand in result.scalars().all()]

    async def get_by_id(self, id: UUID) -> Optional[BrandEntity]:
        stmt = select(Brand).where(Brand.id == id)
        result = await self.session.execute(stmt)
        brand = result.scalars().first()
        if not brand:
            return None
        return self._to_entity(brand)

    async def create(self, brand: BrandEntity) -> BrandEntity:
        db_brand = Brand(
            name=brand.name, country=brand.country, logo_url=brand.logo_url
        )
        self.session.add(db_brand)
        await self.session.commit()
        await self.session.refresh(db_brand)
        return self._to_entity(db_brand)

    async def update(self, brand: BrandEntity) -> BrandEntity:
        stmt = select(Brand).where(Brand.id == brand.id)
        result = await self.session.execute(stmt)
        db_brand = result.scalars().first()
        if not db_brand:
            raise NotFoundError(f"Бренд с ID {brand.id} не найден")

        db_brand.name = brand.name
        db_brand.country = brand.country
        db_brand.logo_url = brand.logo_url

        await self.session.commit()
        await self.session.refresh(db_brand)
        return self._to_entity(db_brand)

    async def delete(self, id: UUID) -> bool:
        stmt = delete(Brand).where(Brand.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0


class ModelRepository(IModelRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Model) -> ModelEntity:
        return ModelEntity(
            id=model.id,
            name=model.name,
            brand_id=model.brand_id,
            year_from=model.year_from,
            year_to=model.year_to,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_all(self, brand_id: Optional[UUID] = None) -> List[ModelEntity]:
        query = select(Model)
        if brand_id:
            query = query.where(Model.brand_id == brand_id)
        query = query.order_by(Model.name)

        result = await self.session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def get_by_id(self, id: UUID) -> Optional[ModelEntity]:
        stmt = select(Model).where(Model.id == id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        if not model:
            return None
        return self._to_entity(model)

    async def create(self, model: ModelEntity) -> ModelEntity:
        db_model = Model(
            name=model.name,
            brand_id=model.brand_id,
            year_from=model.year_from,
            year_to=model.year_to,
        )
        self.session.add(db_model)
        await self.session.commit()
        await self.session.refresh(db_model)
        return self._to_entity(db_model)

    async def update(self, model: ModelEntity) -> ModelEntity:
        stmt = select(Model).where(Model.id == model.id)
        result = await self.session.execute(stmt)
        db_model = result.scalars().first()
        if not db_model:
            raise NotFoundError(f"Модель с ID {model.id} не найдена")

        db_model.name = model.name
        db_model.brand_id = model.brand_id
        db_model.year_from = model.year_from
        db_model.year_to = model.year_to

        await self.session.commit()
        await self.session.refresh(db_model)
        return self._to_entity(db_model)

    async def delete(self, id: UUID) -> bool:
        stmt = delete(Model).where(Model.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0


class CarRepository(ICarRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, car: Car) -> CarEntity:
        return CarEntity(
            id=car.id,
            model_id=car.model_id,
            year=car.year,
            price=car.price,
            mileage=car.mileage,
            condition=car.condition,
            fuel_type=car.fuel_type,
            transmission=car.transmission,
            drive_type=car.drive_type,
            seller_id=car.seller_id,
            color=car.color,
            engine_volume=car.engine_volume,
            power=car.power,
            description=car.description,
            vin=car.vin,
            is_sold=car.is_sold,
            photos=car.photos,
            created_at=car.created_at,
            updated_at=car.updated_at,
        )

    async def get_all(
        self,
        model_id: Optional[UUID] = None,
        brand_id: Optional[UUID] = None,
        condition: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CarEntity]:
        query = select(Car)

        # Применяем фильтры, если они указаны
        filters = []
        if model_id:
            filters.append(Car.model_id == model_id)

        if brand_id:
            # Для фильтрации по бренду нужно присоединить модель
            query = query.join(Model, Car.model_id == Model.id)
            filters.append(Model.brand_id == brand_id)

        if condition:
            filters.append(Car.condition == condition)

        if filters:
            query = query.where(and_(*filters))

        # Применяем пагинацию
        query = query.limit(limit).offset(offset).order_by(Car.created_at.desc())

        result = await self.session.execute(query)
        return [self._to_entity(car) for car in result.scalars().all()]

    async def get_by_id(self, id: UUID) -> Optional[CarEntity]:
        stmt = select(Car).where(Car.id == id)
        result = await self.session.execute(stmt)
        car = result.scalars().first()
        if not car:
            return None
        return self._to_entity(car)

    async def create(self, car: CarEntity) -> CarEntity:
        db_car = Car(
            model_id=car.model_id,
            year=car.year,
            price=car.price,
            mileage=car.mileage,
            condition=car.condition,
            fuel_type=car.fuel_type,
            transmission=car.transmission,
            drive_type=car.drive_type,
            seller_id=car.seller_id,
            color=car.color,
            engine_volume=car.engine_volume,
            power=car.power,
            description=car.description,
            vin=car.vin,
            is_sold=car.is_sold,
            photos=car.photos,
        )
        self.session.add(db_car)
        await self.session.commit()
        await self.session.refresh(db_car)
        return self._to_entity(db_car)

    async def update(self, car: CarEntity) -> CarEntity:
        stmt = select(Car).where(Car.id == car.id)
        result = await self.session.execute(stmt)
        db_car = result.scalars().first()
        if not db_car:
            raise NotFoundError(f"Автомобиль с ID {car.id} не найден")

        # Обновляем все поля
        db_car.model_id = car.model_id
        db_car.year = car.year
        db_car.price = car.price
        db_car.mileage = car.mileage
        db_car.condition = car.condition
        db_car.fuel_type = car.fuel_type
        db_car.transmission = car.transmission
        db_car.drive_type = car.drive_type
        db_car.seller_id = car.seller_id
        db_car.color = car.color
        db_car.engine_volume = car.engine_volume
        db_car.power = car.power
        db_car.description = car.description
        db_car.vin = car.vin
        db_car.is_sold = car.is_sold
        db_car.photos = car.photos

        await self.session.commit()
        await self.session.refresh(db_car)
        return self._to_entity(db_car)

    async def delete(self, id: UUID) -> bool:
        stmt = delete(Car).where(Car.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
