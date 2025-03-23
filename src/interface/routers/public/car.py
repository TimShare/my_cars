from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Response, Query
from interface.dependencies import get_car_service
from interface.schemas.car import CarResponse, ModelResponse, BrandResponse
from core.services import CarService

router = APIRouter(prefix="/public/cars", tags=["public_cars"])


# Полностью публичные эндпоинты (не требуют авторизации)
@router.get("", response_model=List[CarResponse])
async def get_all_cars_public(
    request: Request,
    response: Response,
    model_id: Optional[UUID] = None,
    brand_id: Optional[UUID] = None,
    condition: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    car_service: CarService = Depends(get_car_service),
):
    """Публичное получение списка всех автомобилей с возможностью фильтрации"""
    cars = await car_service.get_all_cars(
        model_id=model_id,
        brand_id=brand_id,
        condition=condition,
        limit=limit,
        offset=offset,
    )
    return [CarResponse.model_validate(car) for car in cars]


@router.get("/{car_id}", response_model=CarResponse)
async def get_car_public(
    car_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service),
):
    """Публичное получение информации об автомобиле по ID"""
    car = await car_service.get_car(car_id)
    return CarResponse.model_validate(car)


@router.get("/brands", response_model=List[BrandResponse])
async def get_all_brands_public(
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service),
):
    """Публичное получение списка всех брендов автомобилей"""
    brands = await car_service.get_all_brands()
    return [BrandResponse.model_validate(brand) for brand in brands]


@router.get("/brands/{brand_id}", response_model=BrandResponse)
async def get_brand_public(
    brand_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service),
):
    """Публичное получение информации о бренде по ID"""
    brand = await car_service.get_brand(brand_id)
    return BrandResponse.model_validate(brand)


@router.get("/models", response_model=List[ModelResponse])
async def get_all_models_public(
    request: Request,
    response: Response,
    brand_id: Optional[UUID] = None,
    car_service: CarService = Depends(get_car_service),
):
    """Публичное получение списка всех моделей автомобилей с фильтрацией по бренду"""
    models = await car_service.get_all_models(brand_id=brand_id)
    return [ModelResponse.model_validate(model) for model in models]


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model_public(
    model_id: UUID,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service),
):
    """Публичное получение информации о модели по ID"""
    model = await car_service.get_model(model_id)
    return ModelResponse.model_validate(model)
