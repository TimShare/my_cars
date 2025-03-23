from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Response, Query, HTTPException, status
from interface.dependencies import get_car_service
from interface.schemas.car import CarCreate, CarUpdate, CarResponse
from core.services import CarService
from core.entites import Car
from interface.routers.decorator import require_scopes

router = APIRouter(prefix="/cars", tags=["cars"])


# Личные объявления пользователя (требуют авторизации)
@router.post("", response_model=CarResponse, status_code=201)
@require_scopes(["car:create"])
async def create_car(
    car_data: CarCreate,
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service),
):
    """Создание нового объявления о продаже автомобиля"""
    # Устанавливаем текущего пользователя как продавца
    if hasattr(request.state, "payload"):
        car_data.seller_id = UUID(request.state.payload.get("sub"))

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
    car_service: CarService = Depends(get_car_service),
):
    """Обновление своего объявления о продаже автомобиля"""
    # Получаем текущие данные
    current_car = await car_service.get_car(car_id)

    # Проверяем, принадлежит ли объявление текущему пользователю
    if hasattr(request.state, "payload"):
        user_id = UUID(request.state.payload.get("sub"))
        if (
            current_car.seller_id != user_id
            and "admin" not in request.state.payload.get("scopes", [])
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете редактировать только свои объявления",
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
    car_service: CarService = Depends(get_car_service),
):
    """Удаление своего объявления о продаже автомобиля"""
    # Получаем текущие данные
    current_car = await car_service.get_car(car_id)

    # Проверяем, принадлежит ли объявление текущему пользователю
    if hasattr(request.state, "payload"):
        user_id = UUID(request.state.payload.get("sub"))
        if (
            current_car.seller_id != user_id
            and "admin" not in request.state.payload.get("scopes", [])
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете удалять только свои объявления",
            )

    await car_service.delete_car(car_id)
    return None


@router.get("/my", response_model=List[CarResponse])
@require_scopes(["car:read"])
async def get_my_cars(
    request: Request,
    response: Response,
    car_service: CarService = Depends(get_car_service),
):
    """Получение списка собственных объявлений пользователя"""
    if hasattr(request.state, "payload"):
        user_id = UUID(request.state.payload.get("sub"))
        # Здесь нужно будет добавить фильтр по seller_id в сервис
        cars = await car_service.get_all_cars(seller_id=user_id)
        return [CarResponse.model_validate(car) for car in cars]
    return []
