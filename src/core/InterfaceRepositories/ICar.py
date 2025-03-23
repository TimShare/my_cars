from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from core.entites import Car, Brand, Model


class IBrandRepository(ABC):
    """Интерфейс репозитория для работы с брендами автомобилей"""

    @abstractmethod
    async def get_all(self) -> List[Brand]:
        """Получение всех брендов"""
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Brand]:
        """Получение бренда по ID"""
        pass

    @abstractmethod
    async def create(self, brand: Brand) -> Brand:
        """Создание нового бренда"""
        pass

    @abstractmethod
    async def update(self, brand: Brand) -> Brand:
        """Обновление информации о бренде"""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Удаление бренда"""
        pass


class IModelRepository(ABC):
    """Интерфейс репозитория для работы с моделями автомобилей"""

    @abstractmethod
    async def get_all(self, brand_id: Optional[UUID] = None) -> List[Model]:
        """Получение всех моделей с возможностью фильтрации по бренду"""
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Model]:
        """Получение модели по ID"""
        pass

    @abstractmethod
    async def create(self, model: Model) -> Model:
        """Создание новой модели"""
        pass

    @abstractmethod
    async def update(self, model: Model) -> Model:
        """Обновление информации о модели"""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Удаление модели"""
        pass


class ICarRepository(ABC):
    """Интерфейс репозитория для работы с автомобилями"""

    @abstractmethod
    async def get_all(
        self,
        model_id: Optional[UUID] = None,
        brand_id: Optional[UUID] = None,
        condition: Optional[str] = None,
        seller_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
        include_brand_model: bool = False,  # Новый параметр
    ) -> List[Car]:
        """Получение списка автомобилей с фильтрацией и возможностью включения данных модели и бренда"""
        pass

    @abstractmethod
    async def get_by_id(
        self, id: UUID, include_brand_model: bool = False
    ) -> Optional[Car]:
        """Получение автомобиля по ID с возможностью включения данных модели и бренда"""
        pass

    @abstractmethod
    async def create(self, car: Car) -> Car:
        """Добавление нового автомобиля"""
        pass

    @abstractmethod
    async def update(self, car: Car) -> Car:
        """Обновление информации об автомобиле"""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Удаление автомобиля"""
        pass
