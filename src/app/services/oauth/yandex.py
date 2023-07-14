from uuid import UUID
import logging
from typing import Any

from pydantic import ValidationError

from abc import ABC, abstractmethod
from common.exceptions.base import OAuthRequestError

from httpx import Response

from wrappers.cache.base import CacheServiceABC

import common.exceptions.auth as auth_exceptions
from schemas.oauth import (
    OAuthTokens,
    OAuthTokensError,
    ResponseStatus,
    OAuthUserInfoSchema,
)

from core.oauth_config import YandexOAuthConfig
from services.oauth.enums import YandexOAuthEndpointEnum
from wrappers.http import AsyncHTTPClientABC
from wrappers.http.exceptions import ClientErrorException

from utils.common import append_query_params_to_url

from domain.oauth.dto import OAuthTokenDto, OAuthUserInfoDto
from domain.oauth.yandex.dto import AuthorizationUrlDto, OAuthRequestTokenDto

from domain.oauth.yandex.request import OAuthRequestTokenSchema
from domain.oauth.yandex.response import (
    OAuthResponseTokenSchema, OAuthUserInfoSchema
)

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
        self._common_request_params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

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
                **self._common_request_params,
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

    # async def refresh_tokens(self, refresh_token):
    #     return await self._post_request(
    #         url=self.token_endpoint,
    #         grant_type="refresh_token",
    #         refresh_token=refresh_token,
    #     )

    # async def revoke_token(self, user_id) -> ResponseStatus:
    #     access_token = await self.cache_client.get_from_cache(f"oauth-{user_id}")
    #     if not access_token:
    #         logger.info("OAuth access token already expire. user_id - {user_id}")
    #         return ResponseStatus(status="ok")
    #     return await self._post_request(
    #         url=self.token_revoke,
    #         response_schema=ResponseStatus,
    #         access_token=access_token,
    #     )

    # async def add_access_token_to_cache(self, user_id, tokens: OAuthTokens):
    #     await self.cache_client.put_to_cache(
    #         f"oauth-{user_id}", tokens.access_token, expire=tokens.expires_in
    #     )
