import logging
from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import ValidationError

from common.exceptions.auth import OAuthTokenExpiredException
from common.exceptions.base import OAuthRequestError
from core.oauth_config import YandexOAuthConfig
from domain.oauth.dto import OAuthTokenDto, OAuthUserInfoDto
from domain.oauth.yandex.dto import (
    AuthorizationUrlDto,
    CacheTokensDto,
    OAuthRequestTokenDto,
    RefreshTokenDto,
    RevokeTokenDto,
)
from domain.oauth.yandex.request import OAuthRequestTokenSchema
from domain.oauth.yandex.response import (
    OAuthResponseRefreshSchema,
    OAuthResponseTokenSchema,
    OAuthUserInfoSchema,
)
from services.oauth.enums import YandexOAuthEndpointEnum
from utils.common import append_query_params_to_url
from wrappers.cache.base import CacheServiceABC
from wrappers.http import AsyncHTTPClientABC
from wrappers.http.exceptions import ClientErrorException

logger = logging.getLogger(__name__)


class YandexOAuthServiceABC(ABC):
    @abstractmethod
    def create_authorization_url(self, auth_url_dto: AuthorizationUrlDto) -> str:
        ...

    @abstractmethod
    async def fetch_token(
        self,
        oauth_request_token: OAuthRequestTokenDto,
    ) -> OAuthTokenDto:
        ...

    @abstractmethod
    async def get_user_info(self, auth_url_dto: AuthorizationUrlDto) -> str:
        ...

    @abstractmethod
    async def user_info(self, token_dto: OAuthTokenDto) -> OAuthUserInfoDto:
        ...

    @abstractmethod
    async def refresh_token(self, user_id: UUID) -> OAuthResponseRefreshSchema:
        ...

    @abstractmethod
    async def revoke_token(self, user_id: UUID) -> None:
        ...

    @abstractmethod
    async def add_tokens_to_cache(self, cache_tokens_dto: CacheTokensDto) -> None:
        ...

    @abstractmethod
    async def remove_tokens_from_cache(self, user_id: UUID) -> None:
        ...


class YandexOAuthService:
    def __init__(
        self,
        cache_client: CacheServiceABC,
        http_client: AsyncHTTPClientABC,
        config: YandexOAuthConfig,
    ) -> None:
        self.config = config
        self.cache_client = cache_client
        self.http_client = http_client

    def create_authorization_url(self, auth_url_dto: AuthorizationUrlDto) -> str:
        """Генерация ссылки для входа в oauth yandex."""
        auth_url_dto.response_type = "code"
        auth_url_dto.client_id = self.config.client_id
        return append_query_params_to_url(
            YandexOAuthEndpointEnum.authorization_endpoint,
            auth_url_dto.as_dict(),
        )

    async def fetch_token(
        self,
        oauth_request_token: OAuthRequestTokenDto,
    ) -> OAuthTokenDto:
        """Получение access токена через oauth yandex."""

        try:
            token_request = OAuthRequestTokenSchema(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                grant_type="authorization_code",
                code=oauth_request_token.code,
            )
            response = await self.http_client.post(
                path=YandexOAuthEndpointEnum.token_endpoint,
                data=token_request.dict(),
            )
            response_token = OAuthResponseTokenSchema(**response)
        except (ValidationError, ClientErrorException) as error:
            logger.error(f"Can't fetch token from oauth yandex. Error={error}")
            raise OAuthRequestError("Some error from fetch token")

        return OAuthTokenDto.from_yandex_response(response_token)

    async def user_info(self, token_dto: OAuthTokenDto) -> OAuthUserInfoDto:
        """Получение информации о пользователе через oauth yandex."""

        try:
            response = await self.http_client.get(
                path=YandexOAuthEndpointEnum.user_info,
                headers={
                    "Authorization": f"OAuth {token_dto.access_token}",
                },
            )
            response_user = OAuthUserInfoSchema(**response)
        except (ValidationError, ClientErrorException) as error:
            logger.error(f"Can't get user info from oauth yandex. Error={error}")
            raise OAuthRequestError("Some error from get user info")

        return OAuthUserInfoDto.from_yandex_response(response_user)

    async def add_tokens_to_cache(self, cache_tokens_dto: CacheTokensDto) -> None:
        """Добавление (и обновление) access и refresh токена в кеш."""
        access_token = cache_tokens_dto.access_token
        refresh_token = cache_tokens_dto.refresh_token
        expired = cache_tokens_dto.expired

        access_cache_key = self.config.access_token_cache_key.format(user_id=cache_tokens_dto.user_id)
        refresh_cache_key = self.config.refresh_token_cache_key.format(user_id=cache_tokens_dto.user_id)

        await self.cache_client.put_to_cache(access_cache_key, access_token, expire=expired)
        await self.cache_client.put_to_cache(refresh_cache_key, refresh_token, expire=expired)

        logger.info(
            f"Yandex oauth access token has been added to cache: {access_cache_key}: {access_token}: {expired}",
        )
        logger.info(
            f"Yandex oauth access token has been added to cache: {refresh_cache_key}: {refresh_token}: {expired}",
        )

    async def remove_tokens_from_cache(self, user_id: UUID) -> None:
        """Удаление access и refresh токена из кеш."""
        access_cache_key = self.config.access_token_cache_key.format(user_id=user_id)
        refresh_cache_key = self.config.refresh_token_cache_key.format(user_id=user_id)

        await self.cache_client.del_from_cache(access_cache_key)
        await self.cache_client.del_from_cache(refresh_cache_key)

        logger.info("Yandex oauth access token has been removed from cache")
        logger.info("Yandex oauth access token has been removed from cache")

    def _create_refresh_token_data(self, refresh_token: str) -> RefreshTokenDto:
        refresh_dto = RefreshTokenDto(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            refresh_token=refresh_token,
            grant_type="refresh_token",
        )
        return refresh_dto

    def _create_revoke_token_data(self, access_token: str) -> RevokeTokenDto:
        refresh_dto = RevokeTokenDto(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            access_token=access_token,
        )
        return refresh_dto

    async def refresh_token(self, user_id: UUID) -> OAuthResponseRefreshSchema:
        """Обновление токена в yandex oauth."""

        cache_key = self.config.refresh_token_cache_key.format(user_id=user_id)
        refresh_token = await self.cache_client.get_from_cache(cache_key)
        if not refresh_token:
            raise OAuthTokenExpiredException
        try:
            refresh_token_data = self._create_refresh_token_data(refresh_token)
            response = await self.http_client.post(
                YandexOAuthEndpointEnum.refresh_endpoint,
                data=refresh_token_data.as_dict(),
            )
            response_refresh = OAuthResponseRefreshSchema(**response)
        except (ValidationError, ClientErrorException) as error:
            logger.error(f"Can't refresh oauth yandex token. Error={error}")
            raise OAuthRequestError("Some error while was refreshing the token")
        return response_refresh

    async def revoke_token(self, user_id: UUID) -> None:
        cache_key = self.config.access_token_cache_key.format(user_id=user_id)
        access_token = await self.cache_client.get_from_cache(cache_key)
        if not access_token:
            raise OAuthTokenExpiredException
        try:
            access_token_data = self._create_revoke_token_data(access_token)
            await self.http_client.post(YandexOAuthEndpointEnum.token_revoke, data=access_token_data.as_dict())
        except (ValidationError, ClientErrorException) as error:
            logger.error(f"Can't refresh oauth yandex token. Error={error}")
            raise OAuthRequestError("Some error while was refreshing the token")
        logger.info("Yandex oauth access token has been revoked")
