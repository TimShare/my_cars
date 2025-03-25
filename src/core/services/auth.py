from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID, uuid4
from core.entites import User, AccessToken, RefreshToken, Token
from core.InterfaceRepositories.IAuth import (
    IAuthRepository,
    IBannedRefreshTokenRepository,
)
from core.exceptions import (
    DuplicateEntryError,
    NotFoundError,
    InvalidCredentialsError,
    TokenExpiredError,
    InvalidTokenError,
    UnauthorizedError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
)
from settings import get_settings
from passlib.context import CryptContext
import jwt


settings = get_settings()


class AuthService:
    def __init__(
        self,
        auth_repository: IAuthRepository,
        banned_refresh_token_repository: IBannedRefreshTokenRepository,
    ):
        self.auth_repository = auth_repository
        self.banned_refresh_token_repository = banned_refresh_token_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_user(self, user: User) -> User:
        """
        Create a new user.
        """
        if await self.auth_repository.get_user(email=user.email):
            raise DuplicateEntryError(
                f"Пользователь с email {user.email} уже существует"
            )

        # Проверка сложности пароля
        if len(user.password) < 8:
            raise ValidationError(
                "Пароль должен содержать минимум 8 символов", field="password"
            )

        user.password = self.pwd_context.hash(user.password)
        return await self.auth_repository.create_user(user)

    async def get_user(self, user_id: str) -> User:
        """
        Get a user by ID.
        """
        try:
            UUID(user_id)  # Проверка на валидность UUID
        except ValueError:
            raise ValidationError(
                "Некорректный формат ID пользователя", field="user_id"
            )

        user = await self.auth_repository.get_user(id=user_id)
        if not user:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")
        return user

    async def get_user_by_email(self, email: str) -> User:
        """
        Get a user by email.
        """
        if not email or "@" not in email:
            raise ValidationError("Некорректный формат email", field="email")

        user = await self.auth_repository.get_user(email=email)
        if not user:
            raise NotFoundError(f"Пользователь с email {email} не найден")
        return user

    async def update_user(self, user: User) -> User:
        """
        Update an existing user.
        """
        existing_user = await self.auth_repository.get_user(id=user.id)
        if not existing_user:
            raise NotFoundError(f"Пользователь с ID {user.id} не найден")

        # Если меняем email, проверяем, что такого еще нет
        if user.email != existing_user.email:
            existing_with_email = await self.auth_repository.get_user(email=user.email)
            if existing_with_email:
                raise DuplicateEntryError(
                    f"Пользователь с email {user.email} уже существует"
                )

        # Если пароль меняется, хешируем его
        if user.password and user.password != existing_user.password:
            if len(user.password) < 8:
                raise ValidationError(
                    "Пароль должен содержать минимум 8 символов", field="password"
                )
            user.password = self.pwd_context.hash(user.password)

        return await self.auth_repository.update_user(user)

    async def login(self, email: str, password: str) -> Token:
        """
        Login a user.
        """
        try:
            user = await self.get_user_by_email(email)
        except NotFoundError:
            # Для безопасности не раскрываем, существует ли пользователь
            raise InvalidCredentialsError("Неверный email или пароль")

        if not self.pwd_context.verify(password, user.password):
            raise InvalidCredentialsError("Неверный email или пароль")

        # Проверка, не заблокирован ли пользователь
        if user.is_blocked:
            raise PermissionDeniedError(
                "Ваш аккаунт заблокирован. Обратитесь к администратору."
            )

        access_token = self.create_access_token(
            {"sub": str(user.id), "scopes": user.scopes}
        )
        refresh_token = self.create_refresh_token(
            {"sub": str(user.id), "jti": str(uuid4())}
        )
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, token: str) -> None:
        """
        Logout a user.
        """
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Срок действия токена истек")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Недействительный токен")

        jti: str = payload.get("jti")
        if not jti:
            raise InvalidTokenError("Неверный формат токена (отсутствует jti)")

        banned_token = (
            await self.banned_refresh_token_repository.create_banned_refresh_token(
                jti=jti
            )
        )
        return banned_token

    async def refresh(self, token: str) -> Token:
        """
        Refresh a user's JWT token.
        """
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Срок действия токена обновления истек")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Недействительный токен обновления")

        # Проверка типа токена
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Неверный тип токена (ожидается refresh)")

        user_id: str = payload.get("sub")
        if user_id is None:
            raise InvalidTokenError("Неверный формат токена (отсутствует sub)")

        try:
            user = await self.auth_repository.get_user(id=UUID(user_id))
        except ValueError:
            raise InvalidTokenError("Некорректный ID пользователя в токене")

        if user is None:
            raise NotFoundError("Пользователь не найден")

        # Проверка, не заблокирован ли пользователь
        if user.is_blocked:
            raise PermissionDeniedError(
                "Ваш аккаунт заблокирован. Обратитесь к администратору."
            )

        jti = payload.get("jti")
        if jti is None:
            raise InvalidTokenError("Неверный формат токена (отсутствует jti)")

        banned_token = (
            await self.banned_refresh_token_repository.is_banned_refresh_token(jti=jti)
        )
        if banned_token:
            raise InvalidTokenError("Токен обновления уже использован или отозван")

        # Добавляем использованный токен в черный список
        await self.banned_refresh_token_repository.create_banned_refresh_token(jti=jti)

        access_token = self.create_access_token(
            {"sub": str(user.id), "scopes": user.scopes}
        )
        refresh_token = self.create_refresh_token(
            {"sub": str(user.id), "jti": str(uuid4())}
        )
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def create_access_token(self, data: dict) -> AccessToken:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return AccessToken(
            token=encoded_jwt,
            type="Bearer",
            expires=timedelta(minutes=settings.access_token_expire_minutes),
        )

    def create_refresh_token(self, data: dict) -> RefreshToken:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )

        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return RefreshToken(
            token=encoded_jwt,
            type="Bearer",
            expires=timedelta(days=settings.refresh_token_expire_days),
            jti=data["jti"],
        )

    async def verify_access_token(self, token: str) -> bool:
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            if payload.get("type") != "access":
                return None
            user_id: str = payload.get("sub")
            if user_id is None:
                return None

            user = await self.auth_repository.get_user(id=UUID(user_id))
            if user is None:
                return None

            # Проверка, не заблокирован ли пользователь
            if user.is_blocked:
                return None

            return True
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def verify_refresh_token(self, token: str) -> bool:
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            if payload.get("type") != "refresh":
                return None

            user_id: str = payload.get("sub")
            if user_id is None:
                return None

            user = await self.auth_repository.get_user(id=UUID(user_id))
            if user is None:
                return None

            # Проверка, не заблокирован ли пользователь
            if user.is_blocked:
                return None

            jti = payload.get("jti")
            if jti is None:
                return None

            banned_token = (
                await self.banned_refresh_token_repository.is_banned_refresh_token(
                    jti=jti
                )
            )
            if banned_token:
                return None

            return True
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # Методы для работы с правами пользователей

    async def add_scopes(self, user_id: str, scopes: List[str]) -> User:
        """
        Добавляет новые права пользователю.
        """
        try:
            user = await self.auth_repository.get_user(id=UUID(user_id))
        except ValueError:
            raise ValidationError(
                "Некорректный формат ID пользователя", field="user_id"
            )

        if not user:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")

        # Проверка валидности скоупов
        valid_scopes = [
            "user:read",
            "user:update",
            "car:read",
            "car:create",
            "car:update",
            "car:delete",
            "admin",
            "admin:car:create",
            "admin:car:update",
            "admin:car:delete",
        ]
        invalid_scopes = [scope for scope in scopes if scope not in valid_scopes]
        if invalid_scopes:
            raise ValidationError(
                f"Неверные права доступа: {', '.join(invalid_scopes)}",
                field="scopes",
                errors={"invalid_scopes": invalid_scopes},
            )

        return await self.auth_repository.add_scopes(user_id, scopes)

    async def update_scopes(self, user_id: str, scopes: List[str]) -> User:
        """
        Полностью заменяет права пользователя.
        """
        try:
            user = await self.auth_repository.get_user(id=UUID(user_id))
        except ValueError:
            raise ValidationError(
                "Некорректный формат ID пользователя", field="user_id"
            )

        if not user:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")

        # Проверка валидности скоупов
        valid_scopes = [
            "user:read",
            "user:update",
            "car:read",
            "car:create",
            "car:update",
            "car:delete",
            "admin",
            "admin:car:create",
            "admin:car:update",
            "admin:car:delete",
        ]
        invalid_scopes = [scope for scope in scopes if scope not in valid_scopes]
        if invalid_scopes:
            raise ValidationError(
                f"Неверные права доступа: {', '.join(invalid_scopes)}",
                field="scopes",
                errors={"invalid_scopes": invalid_scopes},
            )

        return await self.auth_repository.update_scopes(user_id, scopes)

    async def remove_scopes(self, user_id: str, scopes: List[str]) -> User:
        """
        Удаляет указанные права у пользователя.
        """
        try:
            user = await self.auth_repository.get_user(id=UUID(user_id))
        except ValueError:
            raise ValidationError(
                "Некорректный формат ID пользователя", field="user_id"
            )

        if not user:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")

        return await self.auth_repository.remove_scopes(user_id, scopes)

    async def get_user_scopes(self, user_id: str) -> List[str]:
        """
        Получает текущие права пользователя.
        """
        try:
            user = await self.auth_repository.get_user(id=UUID(user_id))
        except ValueError:
            raise ValidationError(
                "Некорректный формат ID пользователя", field="user_id"
            )

        if not user:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")

        return await self.auth_repository.get_user_scopes(user_id)
