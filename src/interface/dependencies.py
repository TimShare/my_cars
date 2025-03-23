import logging
from fastapi import Depends, HTTPException, Request
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from infrastructure.postgres_db import database
from core.services import AuthService, CarService
from infrastructure.repositories import (
    AuthRepository,
    BannedRefreshTokenRepository,
    BrandRepository,
    ModelRepository,
    CarRepository,
)
from settings import get_settings


async def get_auth_service(session: AsyncSession = Depends(database.get_db_session)):
    auth_repository = AuthRepository(session)
    token_repository = BannedRefreshTokenRepository(session)
    service = AuthService(auth_repository, token_repository)
    yield service


async def get_car_service(session: AsyncSession = Depends(database.get_db_session)):
    car_repository = CarRepository(session)
    brand_repository = BrandRepository(session)
    model_repository = ModelRepository(session)
    service = CarService(car_repository, brand_repository, model_repository)
    yield service


settings = get_settings()


class JWTBearer:

    async def __call__(self, request: Request):
        credentials = request.cookies.get("access_token")
        if credentials:
            try:
                payload = jwt.decode(
                    credentials, settings.secret_key, algorithms=[settings.algorithm]
                )
                request.state.payload = payload
                return payload
            except jwt.PyJWTError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No credentials provided"
            )
