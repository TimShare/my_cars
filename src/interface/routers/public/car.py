from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Response, Query, HTTPException, status
from interface.dependencies import get_car_service
from interface.schemas.car import (
    CarCreate, CarUpdate, CarResponse, ModelResponse, BrandResponse
)
from core.services import CarService
from core.entites import Car
from interface.routers.decorator import require_scopes

router = APIRouter(prefix="/cars", tags=["cars"])

# Публичные эндпоинты для автомобилей (требуют только права на чтение)
@router.get("", response_model=List[CarResponse])
@require_scopes(["car:read"])
async def get_all_cars(
    request: Request,
    response: Response,
    model_id: Optional[UUID] = None,
    brand_id: Optional[UUID] = None,
    condition: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    car_service: CarService = Depends(get_car_service)
):
    """Получение списка всех автомобилей с возможностью фильтрации"""
    cars = await car_service.get_all_cars(
        model_id=model_id,
        brand_id=brand_id,
        condition=condition,
        limit=limit,
        offset=offset
    )
    return [CarResponse.model_validate(car) for car in cars]


@router.get("/{car_id}", response_model=CarResponse)
@require_scopes(["car:read"])
async def get_car(
    car_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Получение информации об автомобиле по ID"""
    car = await car_service.get_car(car_id)
    return CarResponse.model_validate(car)


@router.get("/brands", response_model=List[BrandResponse])
@require_scopes(["car:read"])
async def get_all_brands(
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Получение списка всех брендов автомобилей"""
    brands = await car_service.get_all_brands()
    return [BrandResponse.model_validate(brand) for brand in brands]


@router.get("/brands/{brand_id}", response_model=BrandResponse)
@require_scopes(["car:read"])
async def get_brand(
    brand_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Получение информации о бренде по ID"""
    brand = await car_service.get_brand(brand_id)
    return BrandResponse.model_validate(brand)


@router.get("/models", response_model=List[ModelResponse])
@require_scopes(["car:read"])
async def get_all_models(
    request: Request,
    response: Response,
    brand_id: Optional[UUID] = None,
    car_service: CarService = Depends(get_car_service)
):
    """Получение списка всех моделей автомобилей с фильтрацией по бренду"""
    models = await car_service.get_all_models(brand_id=brand_id)
    return [ModelResponse.model_validate(model) for model in models]


@router.get("/models/{model_id}", response_model=ModelResponse)
@require_scopes(["car:read"])
async def get_model(
    model_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Получение информации о модели по ID"""
    model = await car_service.get_model(model_id)
    return ModelResponse.model_validate(model)


# Личные объявления пользователя
@router.post("", response_model=CarResponse, status_code=201)
@require_scopes(["car:create"])
async def create_car(
    car_data: CarCreate,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Создание нового объявления о продаже автомобиля"""
    # Устанавливаем текущего пользователя как продавца
    if hasattr(request.state, 'payload'):
        car_data.seller_id = UUID(request.state.payload.get('sub'))
    
    car = Car(**car_data.model_dump())
    created_car = await car_service.create_car(car)
    return CarResponse.model_validate(created_car)


@router.put("/{car_id}", response_model=CarResponse)
@require_scopes(["car:update"])
async def update_car(
    car_id: UUID,
    car_data: CarUpdate,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Обновление своего объявления о продаже автомобиля"""
    # Получаем текущие данные
    current_car = await car_service.get_car(car_id)
    
    # Проверяем, принадлежит ли объявление текущему пользователю
    if hasattr(request.state, 'payload'):
        user_id = UUID(request.state.payload.get('sub'))
        if current_car.seller_id != user_id and 'admin' not in request.state.payload.get('scopes', []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Вы можете редактировать только свои объявления"
            )
    
    # Обновляем только переданные поля
    update_data = car_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_car, field, value)
    
    updated_car = await car_service.update_car(current_car)
    return CarResponse.model_validate(updated_car)


@router.delete("/{car_id}", status_code=204)
@require_scopes(["car:delete"])
async def delete_car(
    car_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service)
):
    """Удаление своего объявления о продаже автомобиля"""
    # Получаем текущие данные
    current_car = await car_service.get_car(car_id)
    
    # Проверяем, принадлежит ли объявление текущему пользователю
    if hasattr(request.state, 'payload'):
        user_id = UUID(request.state.payload.get('sub'))
        if current_car.seller_id != user_id and 'admin' not in request.state.payload.get('scopes', []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Вы можете удалять только свои объявления"
            )
    
    await car_service.delete_car(car_id)
    return None