from sqlalchemy import select, update
from core.entites import User, BannedRefreshToken
from core.InterfaceRepositories import IAuthRepository, IBannedRefreshTokenRepository
from infrastructure.models import User as UserModel
from infrastructure.models import BannedRefreshToken as BannedRefreshTokenModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.exceptions import NotFoundError


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
            stmt = select(UserModel).filter_by(id=user.id)
            result = await self.session.execute(stmt)
            user_model = result.scalars().first()
            if not user_model:
                raise NotFoundError(f"User with ID {user.id} not found")

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
        except NotFoundError:
            raise
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    async def add_scopes(self, user_id: str, scopes: List[str]) -> User:
        """
        Add new scopes to a user.
        """
        try:
            stmt = select(UserModel).filter_by(id=user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalars().first()
            if not user_model:
                raise NotFoundError(f"User with ID {user_id} not found")

            # Добавляем новые scopes без дубликатов
            current_scopes = set(user_model.scopes)
            current_scopes.update(scopes)
            user_model.scopes = list(current_scopes)

            await self.session.commit()
            await self.session.refresh(user_model)
            return self._to_user(user_model)
        except NotFoundError:
            raise
        except Exception as e:
            print(f"Error adding scopes: {e}")
            return None

    async def update_scopes(self, user_id: str, scopes: List[str]) -> User:
        """
        Replace all scopes of a user.
        """
        try:
            stmt = select(UserModel).filter_by(id=user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalars().first()
            if not user_model:
                raise NotFoundError(f"User with ID {user_id} not found")

            # Полная замена списка scopes
            user_model.scopes = scopes

            await self.session.commit()
            await self.session.refresh(user_model)
            return self._to_user(user_model)
        except NotFoundError:
            raise
        except Exception as e:
            print(f"Error updating scopes: {e}")
            return None

    async def remove_scopes(self, user_id: str, scopes: List[str]) -> User:
        """
        Remove specified scopes from a user.
        """
        try:
            stmt = select(UserModel).filter_by(id=user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalars().first()
            if not user_model:
                raise NotFoundError(f"User with ID {user_id} not found")

            # Удаляем указанные scopes
            user_model.scopes = [s for s in user_model.scopes if s not in scopes]

            await self.session.commit()
            await self.session.refresh(user_model)
            return self._to_user(user_model)
        except NotFoundError:
            raise
        except Exception as e:
            print(f"Error removing scopes: {e}")
            return None

    async def get_user_scopes(self, user_id: str) -> List[str]:
        """
        Get current scopes of a user.
        """
        try:
            stmt = select(UserModel).filter_by(id=user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalars().first()
            if not user_model:
                raise NotFoundError(f"User with ID {user_id} not found")

            return user_model.scopes
        except NotFoundError:
            raise
        except Exception as e:
            print(f"Error getting user scopes: {e}")
            return []


class BannedRefreshTokenRepository(IBannedRefreshTokenRepository):
    # Этот класс оставляем без изменений
    pass
