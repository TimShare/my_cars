import math
from fastapi import APIRouter, Depends, Request, Response
from interface.dependencies import get_auth_service
from interface.schemas.auth import UserLogin
from settings import get_settings
from core.services import AuthService
from core.entites import Token
from starlette import status
from fastapi import HTTPException

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    response: Response,
    user_login: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Login a user and return a JWT token.
    """
    token = await auth_service.login(user_login.email, user_login.password)
    response.set_cookie(
        key="access_token",
        value=token.access_token.token,
        httponly=True,
        secure=False if settings.is_debug_mode else True,
        samesite="Lax",
        max_age=math.ceil(token.access_token.expires.total_seconds()),
    )
    response.set_cookie(
        key="refresh_token",
        value=token.refresh_token.token,
        httponly=True,
        secure=False if settings.is_debug_mode else True,
        samesite="Lax",
        max_age=math.ceil(token.refresh_token.expires.total_seconds()),
    )
    return


@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Logout a user
    """
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.logout(refresh_token)
        response.delete_cookie(key="refresh_token")
    if access_token:
        response.delete_cookie(key="access_token")


@router.get("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Refresh a user's JWT token.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )
    token = await auth_service.refresh(refresh_token)
    response.set_cookie(
        key="access_token",
        value=token.access_token.token,
        httponly=True,
        secure=False if settings.is_debug_mode else True,
        samesite="Lax",
        max_age=math.ceil(token.access_token.expires.total_seconds()),
    )
    response.set_cookie(
        key="refresh_token",
        value=token.refresh_token.token,
        httponly=True,
        secure=False if settings.is_debug_mode else True,
        samesite="Lax",
        max_age=math.ceil(token.refresh_token.expires.total_seconds()),
    )
    return
