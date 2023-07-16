import logging
import uuid
from abc import ABC, abstractmethod

from repositories import SocialAccountRepository, UserRepository
from schemas.response.social_account import SocialAccountResponse
from schemas.response.user import UserResponse

logger = logging.getLogger(__name__)


class SocialAccountServiceABC(ABC):
    @abstractmethod
    async def get_user_by_social_account(self, social_name: str, user_social_id: str) -> UserResponse | None:
        raise NotImplementedError

    @abstractmethod
    async def create_social(self, social_name: str, user_social_id: str, user_id: uuid.UUID) -> SocialAccountResponse:
        raise NotImplementedError


class SocialAccountService(SocialAccountServiceABC):
    def __init__(self, social_account_repository: SocialAccountRepository, user_repository: UserRepository) -> None:
        self._social_account_repository = social_account_repository
        self._user_repository = user_repository

    async def get_user_by_social_account(self, social_name: str, user_social_id: str) -> UserResponse | None:
        social_db = await self._social_account_repository.get_by(social_name=social_name, user_social_id=user_social_id)
        if social_db:
            user_db = await self._user_repository.get_by(id=social_db.user_id)
            return UserResponse.from_orm(user_db)
        return None

    async def create_social(self, social_name: str, user_social_id: str, user_id: uuid.UUID) -> SocialAccountResponse:
        social_db = await self._social_account_repository.create_social(
            social_name=social_name,
            user_social_id=user_social_id,
            user_id=user_id,
        )
        return SocialAccountResponse.from_orm(social_db)
