from typing import List, Optional
from uuid import UUID

from core.entites import Car, Brand, Model
from core.InterfaceRepositories.ICar import (
    ICarRepository,
    IBrandRepository,
    IModelRepository,
)
from core.exceptions import NotFoundError, InvalidRequestError


class CarService:
    def __init__(
        self,
        car_repository: ICarRepository,
        brand_repository: IBrandRepository,
        model_repository: IModelRepository,
    ):
        self.car_repository = car_repository
        self.brand_repository = brand_repository
        self.model_repository = model_repository

    # Методы для работы с брендами
    async def get_all_brands(self) -> List[Brand]:
        return await self.brand_repository.get_all()

    async def get_brand(self, id: UUID) -> Brand:
        brand = await self.brand_repository.get_by_id(id)
        if not brand:
            raise NotFoundError(f"Бренд с ID {id} не найден")
        return brand

    async def create_brand(self, brand: Brand) -> Brand:
        return await self.brand_repository.create(brand)

    async def update_brand(self, brand: Brand) -> Brand:
        # Проверяем, существует ли бренд
        if not await self.brand_repository.get_by_id(brand.id):
            raise NotFoundError(f"Бренд с ID {brand.id} не найден")
        return await self.brand_repository.update(brand)

    async def delete_brand(self, id: UUID) -> bool:
        # Проверяем, существуют ли модели для этого бренда
        models = await self.model_repository.get_all(brand_id=id)
        if models:
            raise InvalidRequestError(
                f"Нельзя удалить бренд, так как существуют связанные модели"
            )

        # Проверяем, существует ли бренд
        if not await self.brand_repository.get_by_id(id):
            raise NotFoundError(f"Бренд с ID {id} не найден")

        return await self.brand_repository.delete(id)

    # Методы для работы с моделями
    async def get_all_models(self, brand_id: Optional[UUID] = None) -> List[Model]:
        return await self.model_repository.get_all(brand_id=brand_id)

    async def get_model(self, id: UUID) -> Model:
        model = await self.model_repository.get_by_id(id)
        if not model:
            raise NotFoundError(f"Модель с ID {id} не найдена")
        return model

    async def create_model(self, model: Model) -> Model:
        # Проверяем, существует ли бренд
        if not await self.brand_repository.get_by_id(model.brand_id):
            raise NotFoundError(f"Бренд с ID {model.brand_id} не найден")

        return await self.model_repository.create(model)

    async def update_model(self, model: Model) -> Model:
        # Проверяем, существует ли модель
        if not await self.model_repository.get_by_id(model.id):
            raise NotFoundError(f"Модель с ID {model.id} не найдена")

        # Проверяем, существует ли бренд
        if not await self.brand_repository.get_by_id(model.brand_id):
            raise NotFoundError(f"Бренд с ID {model.brand_id} не найден")

        return await self.model_repository.update(model)

    async def delete_model(self, id: UUID) -> bool:
        # Проверяем, существуют ли автомобили для этой модели
        cars = await self.car_repository.get_all(model_id=id)
        if cars:
            raise InvalidRequestError(
                f"Нельзя удалить модель, так как существуют связанные автомобили"
            )

        # Проверяем, существует ли модель
        if not await self.model_repository.get_by_id(id):
            raise NotFoundError(f"Модель с ID {id} не найдена")

        return await self.model_repository.delete(id)

    # Методы для работы с автомобилями
    async def get_all_cars(
        self,
        model_id: Optional[UUID] = None,
        brand_id: Optional[UUID] = None,
        condition: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Car]:
        return await self.car_repository.get_all(
            model_id=model_id,
            brand_id=brand_id,
            condition=condition,
            limit=limit,
            offset=offset,
        )

    async def get_car(self, id: UUID) -> Car:
        car = await self.car_repository.get_by_id(id)
        if not car:
            raise NotFoundError(f"Автомобиль с ID {id} не найден")
        return car

    async def create_car(self, car: Car) -> Car:
        # Проверяем, существует ли модель
        if not await self.model_repository.get_by_id(car.model_id):
            raise NotFoundError(f"Модель с ID {car.model_id} не найдена")

        return await self.car_repository.create(car)

    async def update_car(self, car: Car) -> Car:
        # Проверяем, существует ли автомобиль
        if not await self.car_repository.get_by_id(car.id):
            raise NotFoundError(f"Автомобиль с ID {car.id} не найден")

        # Проверяем, существует ли модель
        if not await self.model_repository.get_by_id(car.model_id):
            raise NotFoundError(f"Модель с ID {car.model_id} не найдена")

        return await self.car_repository.update(car)

    async def delete_car(self, id: UUID) -> bool:
        # Проверяем, существует ли автомобиль
        if not await self.car_repository.get_by_id(id):
            raise NotFoundError(f"Автомобиль с ID {id} не найден")

        return await self.car_repository.delete(id)
