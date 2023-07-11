import jwt

from typing import Optional
import logging
from uuid import UUID
from abc import ABC, abstractmethod

from datetime import datetime, timedelta
from schemas.auth import AuthData, RefreshData

from wrappers.cache.base import CacheServiceABC

from common.constants import EXPIRE_ACCESS_TOKEN, EXPIRE_REFRESH_TOKEN
import common.exceptions.auth as auth_exceptions
from schemas.response.token import TokensResponse

logger = logging.getLogger(__name__)


class AuthServiceABC(ABC):

    @abstractmethod
    async def create_access_token(self, user_id: UUID, is_superuser: bool = False) -> str:
        ...

    @abstractmethod
    async def create_token_pair(self, user_id: UUID, is_superuser: bool = False) -> TokensResponse:
        ...

    @abstractmethod
    async def create_refresh_token(self, user_id: UUID, is_superuser: bool = False) -> str:
        ...

    @abstractmethod
    async def validate_access_token(self, access_token: str) -> AuthData:
        ...

    @abstractmethod
    async def validate_refresh_token(self, refresh_token: str) -> RefreshData:
        ...

    @abstractmethod
    async def remove_refresh_token_from_cache(self, refresh_token: str) -> None:
        ...


class AuthService(AuthServiceABC):
    encode_algorithm: str = "HS256"

    def __init__(self, cache_client: CacheServiceABC, jwt_secret_key: str) -> None:
        self.jwt_secret_key = jwt_secret_key
        self.cache_client = cache_client

    async def create_token_pair(self, user_id: UUID, is_superuser: bool = False) -> TokensResponse:
        access_token = await self.create_access_token(user_id, is_superuser)
        refresh_token = await self.create_refresh_token(user_id, is_superuser)
        return TokensResponse(access_token=access_token, refresh_token=refresh_token)

    def _create_token(
            self,
            expire_timestamp: int,
            user_id: Optional[UUID] = None,
            is_superuser: Optional[bool] = None,
    ) -> str:
        payload = {
            'sub': 'authentication',
            'exp': expire_timestamp,
            'iat': int(datetime.utcnow().timestamp()),
        }
        if user_id is not None:
            payload['user_id'] = str(user_id)
        if is_superuser is not None:
            payload['is_superuser'] = str(is_superuser)

        try:
            token = jwt.encode(payload, self.jwt_secret_key, algorithm=self.encode_algorithm)
        except (ValueError, TypeError):
            logger.error("Can't create jwt token! See JWT_SECRET_KEY env, or something else...",
                         exc_info=True)
            raise auth_exceptions.TokenEncodeException()

        return token

    def _validate_token(self, token: str) -> dict:

        try:
            payload: dict = jwt.decode(token, self.jwt_secret_key, algorithms=[self.encode_algorithm])
        except (
                jwt.DecodeError,
                jwt.InvalidKeyError,
                jwt.InvalidIssuerError,
                jwt.InvalidSignatureError,
        ):
            logger.error(f"Can't decode jwt token! See {token}")
            raise auth_exceptions.TokenDecodeException()
        except jwt.exceptions.ExpiredSignatureError as error:
            logger.warning(f"Token is expired! error = {error}")
            raise auth_exceptions.TokenExpiredException()

        logger.info(">>> Payload %s", payload)

        return payload

    async def create_refresh_token(self, user_id: UUID, is_superuser: bool = False) -> str:
        """Генерация refresh токена и запись в кеш."""

        refresh_expire = (datetime.now() + timedelta(seconds=EXPIRE_REFRESH_TOKEN)).timestamp()
        refresh_token = self._create_token(expire_timestamp=int(refresh_expire),
                                           user_id=user_id,
                                           is_superuser=is_superuser)

        await self.cache_client.put_to_cache(key=refresh_token, value=str(user_id), expire=EXPIRE_REFRESH_TOKEN)

        return refresh_token

    async def create_access_token(self, user_id: UUID, is_superuser: bool = False) -> str:
        """Генерация access токена."""

        access_expire = (datetime.now() + timedelta(seconds=EXPIRE_ACCESS_TOKEN)).timestamp()
        access_token = self._create_token(
            expire_timestamp=int(access_expire),
            user_id=user_id,
            is_superuser=is_superuser,
        )

        return access_token

    async def validate_access_token(self, access_token: str) -> AuthData:
        """Валидация access токена."""
        payload = self._validate_token(access_token)
        user_id = payload.get('user_id')
        is_superuser = payload.get('is_superuser', False)
        if not user_id:
            logger.error(f"Can't get user_id from access token! {access_token}")
            raise auth_exceptions.TokenDecodeException()

        return AuthData(user_id=UUID(user_id), is_superuser=is_superuser)

    async def validate_refresh_token(self, refresh_token: str) -> RefreshData:
        """Валидация refresh токена."""
        payload = self._validate_token(refresh_token)
        user_id = payload.get('user_id')
        is_superuser = payload.get('is_superuser', False)

        # Проверим одноразовость токена
        if not await self.cache_client.get_from_cache(refresh_token):
            logger.error(f"Can't get token from cache! {refresh_token}")
            raise auth_exceptions.TokenException()

        return RefreshData(
            user_id=user_id,
            is_superuser=is_superuser,
            refresh_token=refresh_token,
        )

    async def remove_refresh_token_from_cache(self, refresh_token: str) -> None:
        """Удаление токена из БД."""
        await self.cache_client.del_from_cache(refresh_token)
