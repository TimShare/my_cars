from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from core.entites import User, AccessToken, RefreshToken, Token


class IAuthRepository(ABC):
    """
    Interface for the authentication repository.
    """

    @abstractmethod
    async def create_user(self, user: User) -> User:
        """
        Create a new user.
        """
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> User:
        """
        Get a user by ID.
        """
        pass

    @abstractmethod
    async def update_user(self, user: User) -> User:
        """
        Update an existing user.
        """
        pass

    @abstractmethod
    async def add_scopes(self, user_id: str, scopes: List[str]) -> User:
        """
        Add new scopes to a user.
        """
        pass

    @abstractmethod
    async def update_scopes(self, user_id: str, scopes: List[str]) -> User:
        """
        Replace all scopes of a user.
        """
        pass

    @abstractmethod
    async def remove_scopes(self, user_id: str, scopes: List[str]) -> User:
        """
        Remove specified scopes from a user.
        """
        pass

    @abstractmethod
    async def get_user_scopes(self, user_id: str) -> List[str]:
        """
        Get current scopes of a user.
        """
        pass


class IBannedRefreshTokenRepository(ABC):
    """
    Interface for the banned refresh token repository.
    """

    @abstractmethod
    async def create_banned_refresh_token(self, jti: UUID) -> None:
        """
        Create a new banned refresh token.
        """
        pass

    @abstractmethod
    async def is_banned_refresh_token(self, jti: UUID) -> bool:
        """
        Check if a refresh token is banned.
        """
        pass
