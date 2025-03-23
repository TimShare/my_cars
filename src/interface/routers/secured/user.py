from fastapi import APIRouter, Depends, Request, Response
from interface.dependencies import get_auth_service
from interface.schemas.auth import UserCreate, UserResponse
from core.services import AuthService
from core.entites import User
from interface.routers.decorator import require_scopes

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create")
@require_scopes(["user:create"])
async def create_user(
    user: UserCreate,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Create a new user.
    """
    user = User(**user.model_dump())
    user = await auth_service.create_user(user)
    return UserResponse.model_validate(user)


@router.get("/get/{user_id}")
@require_scopes(["user:get"])
async def get_user(
    user_id: str,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get a user by ID.
    """
    user = await auth_service.get_user(user_id)
    return UserResponse.model_validate(user)
