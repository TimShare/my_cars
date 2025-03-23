from sqlalchemy import select
from core.entites import User, BannedRefreshToken
from core.InterfaceRepositories import IAuthRepository, IBannedRefreshTokenRepository
from infrastructure.models import User as UserModel
from infrastructure.models import BannedRefreshToken as BannedRefreshTokenModel
from sqlalchemy.ext.asyncio import AsyncSession


class AuthRepository(IAuthRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_user(self, user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            email=user_model.email,
            password=user_model.password,
            name=user_model.name,
            surname=user_model.surname,
            is_active=user_model.is_active,
            is_superuser=user_model.is_superuser,
            scopes=user_model.scopes,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
        )

    async def get_user(self, **filters) -> User | None:
        """ "
        Get a user by filters.
        """
        try:
            stmt = select(UserModel).filter_by(**filters)
            result = await self.session.execute(stmt)
            user = result.scalars().first()
            if not user:
                return None
            return self._to_user(user)
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    async def create_user(self, user: User) -> User:
        """
        Create a new user.
        """
        try:
            user_model = UserModel(
                email=user.email,
                password=user.password,
                name=user.name,
                surname=user.surname,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                scopes=user.scopes,
            )
            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)
            return self._to_user(user_model)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    async def update_user(self, user: User) -> User:
        """
        Update an existing user.
        """
        try:
            user_model = await self.get_user(id=user.id)
            if not user_model:
                raise ValueError("User not found")
            user_model.email = user.email
            user_model.password = user.password
            user_model.name = user.name
            user_model.surname = user.surname
            user_model.is_active = user.is_active
            user_model.is_superuser = user.is_superuser
            user_model.scopes = user.scopes
            await self.session.commit()
            await self.session.refresh(user_model)
            return self._to_user(user_model)
        except Exception as e:
            print(f"Error updating user: {e}")
            return None


class BannedRefreshTokenRepository(IBannedRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_banned_refresh_token(self, jti: str) -> None:
        """
        Create a new banned refresh token.
        """
        try:
            banned_refresh_token = BannedRefreshTokenModel(jti=jti)
            self.session.add(banned_refresh_token)
            await self.session.commit()
        except Exception as e:
            print(f"Error creating banned refresh token: {e}")

    async def is_banned_refresh_token(self, jti: str) -> bool:
        """
        Check if a refresh token is banned.
        """
        try:
            stmt = select(BannedRefreshTokenModel).filter_by(jti=jti)
            result = await self.session.execute(stmt)
            return result.scalars().first() is not None
        except Exception as e:
            print(f"Error checking banned refresh token: {e}")
            return False
