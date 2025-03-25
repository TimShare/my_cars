from typing import List, Optional
from uuid import UUID

from core.entites import Car, Brand, Model
from core.InterfaceRepositories.ICar import (
    ICarRepository,
    IBrandRepository,
    IModelRepository,
)
from core.exceptions import (
    NotFoundError,
    InvalidRequestError,
    BrandModelMismatchError,
    CarNotAvailableError,
    ModelYearError,
    InvalidVINError,
    DuplicateVINError,
    InvalidPriceError,
    TooManyListingsError,
)


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
        # Проверка на дубликаты по имени
        existing_brands = await self.brand_repository.get_all()
        for existing_brand in existing_brands:
            if existing_brand.name.lower() == brand.name.lower():
                raise DuplicateEntryError(
                    f"Бренд с названием '{brand.name}' уже существует"
                )

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
        brand = await self.brand_repository.get_by_id(model.brand_id)
        if not brand:
            raise NotFoundError(f"Бренд с ID {model.brand_id} не найден")

        # Проверка на дубликаты в рамках одного бренда
        existing_models = await self.model_repository.get_all(brand_id=model.brand_id)
        for existing_model in existing_models:
            if existing_model.name.lower() == model.name.lower():
                raise DuplicateEntryError(
                    f"Модель '{model.name}' уже существует для бренда '{brand.name}'"
                )

        # Проверка года выпуска
        if model.year_from and model.year_to and model.year_from > model.year_to:
            raise InvalidDateRangeError(
                f"Неверный диапазон годов производства: год начала ({model.year_from}) больше года окончания ({model.year_to})",
                field="year_range",
            )

        return await self.model_repository.create(model)

    async def update_model(self, model: Model) -> Model:
        # Проверяем, существует ли модель
        if not await self.model_repository.get_by_id(model.id):
            raise NotFoundError(f"Модель с ID {model.id} не найдена")

        # Проверяем, существует ли бренд
        if not await self.brand_repository.get_by_id(model.brand_id):
            raise NotFoundError(f"Бренд с ID {model.brand_id} не найден")

        # Проверка года выпуска
        if model.year_from and model.year_to and model.year_from > model.year_to:
            raise InvalidDateRangeError(
                f"Неверный диапазон годов производства: год начала ({model.year_from}) больше года окончания ({model.year_to})",
                field="year_range",
            )

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
        seller_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
        include_brand_model: bool = True,
    ) -> List[Car]:
        """
        Получение списка автомобилей с информацией о моделях и брендах
        """
        return await self.car_repository.get_all(
            model_id=model_id,
            brand_id=brand_id,
            condition=condition,
            seller_id=seller_id,
            limit=limit,
            offset=offset,
            include_brand_model=include_brand_model,
        )

    async def get_car(self, id: UUID, include_brand_model: bool = True) -> Car:
        """
        Получение информации об автомобиле по ID с информацией о модели и бренде
        """
        car = await self.car_repository.get_by_id(
            id, include_brand_model=include_brand_model
        )
        if not car:
            raise NotFoundError(f"Автомобиль с ID {id} не найден")
        return car

    async def create_car(self, car: Car) -> Car:
        # Проверяем, существует ли модель
        model = await self.model_repository.get_by_id(car.model_id)
        if not model:
            raise NotFoundError(f"Модель с ID {car.model_id} не найдена")

        # Проверяем соответствие года выпуска автомобиля диапазону годов модели
        if model.year_from and car.year < model.year_from:
            raise ModelYearError(
                f"Год выпуска автомобиля ({car.year}) меньше начального года производства модели ({model.year_from})",
                year_from=model.year_from,
                year_to=model.year_to,
            )

        if model.year_to and car.year > model.year_to:
            raise ModelYearError(
                f"Год выпуска автомобиля ({car.year}) больше конечного года производства модели ({model.year_to})",
                year_from=model.year_from,
                year_to=model.year_to,
            )

        # Проверка валидности VIN
        if car.vin:
            if len(car.vin) != 17:
                raise InvalidVINError("VIN номер должен содержать ровно 17 символов")

            # Проверка уникальности VIN
            existing_cars = await self.car_repository.get_all()
            for existing_car in existing_cars:
                if existing_car.vin and existing_car.vin.lower() == car.vin.lower():
                    raise DuplicateVINError(
                        f"Автомобиль с VIN номером {car.vin} уже существует в системе"
                    )

        # Проверка цены
        if car.price <= 0:
            raise InvalidPriceError(
                "Цена автомобиля должна быть положительной", min_price=1
            )

        # Проверка лимита объявлений пользователя
        if car.seller_id:
            user_cars_count = len(
                await self.car_repository.get_all(seller_id=car.seller_id)
            )
            max_listings = 10  # Пример лимита объявлений
            if user_cars_count >= max_listings:
                raise TooManyListingsError(
                    f"Превышен лимит активных объявлений ({max_listings})",
                    max_listings=max_listings,
                )

        return await self.car_repository.create(car)

    async def update_car(self, car: Car) -> Car:
        # Проверяем, существует ли автомобиль
        existing_car = await self.car_repository.get_by_id(car.id)
        if not existing_car:
            raise NotFoundError(f"Автомобиль с ID {car.id} не найден")

        # Проверка, не продан ли автомобиль
        if existing_car.is_sold:
            raise CarNotAvailableError(
                "Нельзя обновить информацию о проданном автомобиле"
            )

        # Проверяем, существует ли модель
        model = await self.model_repository.get_by_id(car.model_id)
        if not model:
            raise NotFoundError(f"Модель с ID {car.model_id} не найдена")

        # Проверяем соответствие года выпуска автомобиля диапазону годов модели
        if model.year_from and car.year < model.year_from:
            raise ModelYearError(
                f"Год выпуска автомобиля ({car.year}) меньше начального года производства модели ({model.year_from})",
                year_from=model.year_from,
                year_to=model.year_to,
            )

        if model.year_to and car.year > model.year_to:
            raise ModelYearError(
                f"Год выпуска автомобиля ({car.year}) больше конечного года производства модели ({model.year_to})",
                year_from=model.year_from,
                year_to=model.year_to,
            )

        # Проверка валидности VIN, если он изменился
        if car.vin and (not existing_car.vin or existing_car.vin != car.vin):
            if len(car.vin) != 17:
                raise InvalidVINError("VIN номер должен содержать ровно 17 символов")

            # Проверка уникальности VIN
            existing_cars = await self.car_repository.get_all()
            for other_car in existing_cars:
                if (
                    other_car.id != car.id
                    and other_car.vin
                    and other_car.vin.lower() == car.vin.lower()
                ):
                    raise DuplicateVINError(
                        f"Автомобиль с VIN номером {car.vin} уже существует в системе"
                    )

        # Проверка цены
        if car.price <= 0:
            raise InvalidPriceError(
                "Цена автомобиля должна быть положительной", min_price=1
            )

        return await self.car_repository.update(car)

    async def delete_car(self, id: UUID) -> bool:
        # Проверяем, существует ли автомобиль
        car = await self.car_repository.get_by_id(id)
        if not car:
            raise NotFoundError(f"Автомобиль с ID {id} не найден")

        # Проверка, не продан ли автомобиль
        if car.is_sold:
            raise CarNotAvailableError(
                "Нельзя удалить объявление о проданном автомобиле"
            )

        return await self.car_repository.delete(id)

    async def mark_car_as_sold(self, id: UUID) -> Car:
        """Отметить автомобиль как проданный"""
        car = await self.car_repository.get_by_id(id)
        if not car:
            raise NotFoundError(f"Автомобиль с ID {id} не найден")

        if car.is_sold:
            raise CarNotAvailableError("Автомобиль уже отмечен как проданный")

        car.is_sold = True
        return await self.car_repository.update(car)
