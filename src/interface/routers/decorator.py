import functools
from typing import List, Callable
from fastapi import Depends, HTTPException, Request
from starlette import status
from interface.dependencies import get_auth_service
from core.services import AuthService
from uuid import UUID


def require_scopes(required_scopes: List[str]) -> Callable:
    """
    Декоратор для проверки прав доступа пользователя.
    Администраторы (is_admin=True или имеющие scope 'admin') автоматически пропускаются.

    Args:
        required_scopes: Список необходимых прав доступа

    Returns:
        Декоратор, который проверяет наличие необходимых прав у пользователя
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(
            request: Request,
            auth_service: AuthService = Depends(get_auth_service),
            *args,
            **kwargs,
        ):
            try:
                # Получаем payload из request.state.payload
                payload = request.state.payload

                # Проверяем, является ли пользователь администратором
                user_scopes = payload.get("scopes", [])
                is_admin = payload.get("is_admin", False) or "admin" in user_scopes

                # Если пользователь не администратор, проверяем права доступа
                if not is_admin and not set(required_scopes).issubset(set(user_scopes)):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Недостаточно прав доступа. Требуются: {', '.join(required_scopes)}",
                    )

                # Получение ID пользователя из payload
                user_id = payload.get("sub")

                # Получение информации о пользователе
                user = await auth_service.get_user(user_id)

                # Добавление информации о пользователе в запрос
                request.state.user = user

                return await func(
                    request=request, auth_service=auth_service, *args, **kwargs
                )

            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Ошибка аутентификации",
                )

        return wrapper

    return decorator
