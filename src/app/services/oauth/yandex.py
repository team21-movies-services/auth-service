from uuid import UUID
import logging
from typing import Any

from abc import ABC, abstractmethod

import httpx
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
from utils.common import append_query_params_to_url

from domain.oauth.yandex.dto import AuthorizationUrlDto

logger = logging.getLogger(__name__)


class YandexOAuthServiceABC:

    def create_authorization_url(self, redirect_uri: str, device_id: UUID) -> str:
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

    def create_authorization_url(self, redirect_uri: str, device_id: UUID) -> str:
        auth_url_dto = AuthorizationUrlDto(
            response_type="code",
            client_id=self.config.client_id,
            redirect_uri=redirect_uri,
            device_id=device_id,
        )
        return append_query_params_to_url(YandexOAuthEndpointEnum.authorization_endpoint, auth_url_dto.as_dict())

    # async def _post_request(
    #     self, url: str, response_schema: Any = OAuthTokens, **kwargs
    # ):
    #     async with httpx.AsyncClient() as client:
    #         r: Response = await client.post(
    #             url,
    #             data={
    #                 "client_id": self.config.client_id,
    #                 "client_secret": self.config.client_secret,
    #                 **kwargs,
    #             },
    #         )
    #         if r.status_code == httpx.codes.OK:
    #             return response_schema(**r.json())

    #         err = OAuthTokensError(**r.json())
    #         logger.error(f"Request to token: {kwargs}. Error: {err.log_error()}")
    #         raise auth_exceptions.OAuthException(err.log_error())

    # async def fetch_token(self, code: str, state: str | None = None):
    #     return await self._post_request(
    #         url=self.token_endpoint,
    #         grant_type="authorization_code",
    #         code=code,
    #     )

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

    # async def user_info(self, access_token):
    #     async with httpx.AsyncClient() as client:
    #         r: Response = await client.get(
    #             self.userinfo,
    #             headers={
    #                 "Authorization": f"OAuth {access_token}",
    #             },
    #         )
    #         if r.status_code == httpx.codes.OK:
    #             return OAuthUserInfoSchema.from_yandex(**r.json())
    #         logger.error(f"Request to userinfo: {r.status_code}. Error: {r.text}")
    #         raise auth_exceptions.OAuthException()
