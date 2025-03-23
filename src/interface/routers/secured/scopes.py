from fastapi import APIRouter, Depends, Request, Response, Path
from typing import List
from uuid import UUID
from interface.dependencies import get_auth_service
from interface.schemas import ScopesRequest, ScopesResponse, UserResponse
from core.services import AuthService
from interface.routers.decorator import require_scopes

router = APIRouter(prefix="/scopes", tags=["scopes"])


@router.post("/users/{user_id}/scopes", response_model=ScopesResponse)
@require_scopes(["admin"])
async def add_scopes(
    user_id: UUID = Path(..., description="ID пользователя"),
    scopes_request: ScopesRequest = None,
    request: Request = None,
    response: Response = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Добавляет новые права пользователю.
    Требуется право admin.
    """
    user = await auth_service.add_scopes(str(user_id), scopes_request.scopes)
    return ScopesResponse(scopes=user.scopes, user_id=user.id)


@router.put("/users/{user_id}/scopes", response_model=ScopesResponse)
@require_scopes(["admin"])
async def update_scopes(
    user_id: UUID = Path(..., description="ID пользователя"),
    scopes_request: ScopesRequest = None,
    request: Request = None,
    response: Response = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Полностью заменяет права пользователя.
    Требуется право admin.
    """
    user = await auth_service.update_scopes(str(user_id), scopes_request.scopes)
    return ScopesResponse(scopes=user.scopes, user_id=user.id)


@router.delete("/users/{user_id}/scopes", response_model=ScopesResponse)
@require_scopes(["admin"])
async def remove_scopes(
    user_id: UUID = Path(..., description="ID пользователя"),
    scopes_request: ScopesRequest = None,
    request: Request = None,
    response: Response = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Удаляет указанные права у пользователя.
    Требуется право admin.
    """
    user = await auth_service.remove_scopes(str(user_id), scopes_request.scopes)
    return ScopesResponse(scopes=user.scopes, user_id=user.id)


@router.get("/users/{user_id}/scopes", response_model=ScopesResponse)
@require_scopes(["admin"])
async def get_user_scopes(
    user_id: UUID = Path(..., description="ID пользователя"),
    request: Request = None,
    response: Response = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Получает текущие права пользователя.
    Требуется право admin.
    """
    scopes = await auth_service.get_user_scopes(str(user_id))
    return ScopesResponse(scopes=scopes, user_id=user_id)


@router.get("/me/scopes", response_model=ScopesResponse)
@require_scopes(["user:read"])
async def get_my_scopes(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Получает права текущего пользователя.
    Требуется право user:read.
    """
    user_id = request.state.payload.get("sub")
    scopes = await auth_service.get_user_scopes(user_id)
    return ScopesResponse(scopes=scopes, user_id=UUID(user_id))
