from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Response
from interface.dependencies import get_car_service
from interface.schemas.car import (
    BrandCreate, BrandUpdate, BrandResponse,
    ModelCreate, ModelUpdate, ModelResponse,
    CarResponse, CarUpdate
)
from core.services import CarService
from core.entites import Brand, Model
from interface.routers.decorator import require_scopes

router = APIRouter(prefix="/admin/cars", tags=["admin_cars"])

# Административные эндпоинты для брендов
@router.post("/brands", response_model=BrandResponse, status_code=201)
@require_scopes(["admin:car:create"])
async def admin_create_brand(
    brand_data: BrandCreate,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Создание нового бренда (только администратор)"""
    brand = Brand(**brand_data.model_dump())
    created_brand = await car_service.create_brand(brand)
    return BrandResponse.model_validate(created_brand)


@router.put("/brands/{brand_id}", response_model=BrandResponse)
@require_scopes(["admin:car:update"])
async def admin_update_brand(
    brand_id: UUID,
    brand_data: BrandUpdate,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Обновление информации о бренде (только администратор)"""
    # Получаем текущие данные
    current_brand = await car_service.get_brand(brand_id)
    
    # Обновляем только переданные поля
    update_data = brand_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_brand, field, value)
    
    updated_brand = await car_service.update_brand(current_brand)
    return BrandResponse.model_validate(updated_brand)


@router.delete("/brands/{brand_id}", status_code=204)
@require_scopes(["admin:car:delete"])
async def admin_delete_brand(
    brand_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Удаление бренда (только администратор)"""
    await car_service.delete_brand(brand_id)
    return None


# Административные эндпоинты для моделей
@router.post("/models", response_model=ModelResponse, status_code=201)
@require_scopes(["admin:car:create"])
async def admin_create_model(
    model_data: ModelCreate,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Создание новой модели (только администратор)"""
    model = Model(**model_data.model_dump())
    created_model = await car_service.create_model(model)
    return ModelResponse.model_validate(created_model)


@router.put("/models/{model_id}", response_model=ModelResponse)
@require_scopes(["admin:car:update"])
async def admin_update_model(
    model_id: UUID,
    model_data: ModelUpdate,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Обновление информации о модели (только администратор)"""
    # Получаем текущие данные
    current_model = await car_service.get_model(model_id)
    
    # Обновляем только переданные поля
    update_data = model_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_model, field, value)
    
    updated_model = await car_service.update_model(current_model)
    return ModelResponse.model_validate(updated_model)


@router.delete("/models/{model_id}", status_code=204)
@require_scopes(["admin:car:delete"])
async def admin_delete_model(
    model_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Удаление модели (только администратор)"""
    await car_service.delete_model(model_id)
    return None


# Административные эндпоинты для управления любыми объявлениями
@router.put("/listings/{car_id}", response_model=CarResponse)
@require_scopes(["admin:car:update"])
async def admin_update_car(
    car_id: UUID,
    car_data: CarUpdate,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Обновление любого объявления (только администратор)"""
    # Получаем текущие данные
    current_car = await car_service.get_car(car_id)
    
    # Обновляем только переданные поля
    update_data = car_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_car, field, value)
    
    updated_car = await car_service.update_car(current_car)
    return CarResponse.model_validate(updated_car)


@router.delete("/listings/{car_id}", status_code=204)
@require_scopes(["admin:car:delete"])
async def admin_delete_car(
    car_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Удаление любого объявления (только администратор)"""
    await car_service.delete_car(car_id)
    return None