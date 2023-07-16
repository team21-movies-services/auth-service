import logging
from abc import ABC, abstractmethod
from uuid import UUID

import jwt
from pydantic import ValidationError

from common.exceptions.auth import OAuthTokenExpiredException
from common.exceptions.base import OAuthRequestError
from core.oauth_config import GoogleOAuthConfig
from domain.oauth.dto import OAuthUserInfoDto
from domain.oauth.google.dto import (
    AccessTokenDto,
    AuthorizationUrlDto,
    RefreshTokenDto,
    RevokeTokenUrlDto,
)
from domain.oauth.google.response import (
    GoogleOAuthPairTokensResponseSchema,
    GoogleOAuthResponseRefreshSchema,
    GoogleOAuthResponseTokenSchema,
    GoogleOAuthResponseUserInfoSchema,
)
from services.oauth.enums import GoogleOAuthEndpointEnum
from utils.common import append_query_params_to_url
from wrappers.cache.base import CacheServiceABC
from wrappers.http import AsyncHTTPClientABC
from wrappers.http.exceptions import ClientErrorException

logger = logging.getLogger(__name__)


class GoogleOAuthServiceABC(ABC):
    @abstractmethod
    def create_authorization_url(self, redirect_uri: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def fetch_access_token(self, redirect_uri: str, code: str) -> GoogleOAuthResponseTokenSchema:
        raise NotImplementedError

    @abstractmethod
    async def fetch_user_info(self, vk_access_info: GoogleOAuthResponseTokenSchema) -> OAuthUserInfoDto:
        raise NotImplementedError

    @abstractmethod
    async def add_access_token_to_cache(self, user_id: UUID, access_token: str, expires_in: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_access_token_from_cache(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_refresh_token_from_cache(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_refresh_token_to_cache(self, user_id: UUID, refresh_token: str, expires_in: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_refresh_token_cache_expire(self, user_id: UUID, expires_in: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def revoke_token(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def refresh_token(self, user_id: UUID) -> GoogleOAuthResponseRefreshSchema:
        raise NotImplementedError

    @abstractmethod
    async def get_tokens_pair(self, user_id: UUID) -> GoogleOAuthPairTokensResponseSchema:
        raise NotImplementedError


class GoogleOAuthService(GoogleOAuthServiceABC):
    def __init__(
        self,
        cache_client: CacheServiceABC,
        http_client: AsyncHTTPClientABC,
        config: GoogleOAuthConfig,
    ) -> None:
        self._config = config
        self._cache_client = cache_client
        self._http_client = http_client

    def create_authorization_url(self, redirect_uri: str) -> str:
        auth_url_dto = AuthorizationUrlDto(
            response_type="code",
            client_id=self._config.client_id,
            redirect_uri=redirect_uri,
            scope="openid email profile",
            access_type="offline",
        )
        return append_query_params_to_url(GoogleOAuthEndpointEnum.authorization_endpoint, auth_url_dto.as_dict())

    def _create_access_token_data(self, redirect_uri: str, code: str) -> AccessTokenDto:
        access_url_dto = AccessTokenDto(
            client_id=self._config.client_id,
            client_secret=self._config.client_secret,
            redirect_uri=redirect_uri,
            code=code,
            grant_type="authorization_code",
        )
        return access_url_dto

    def _create_refresh_token_data(self, refresh_token: str) -> RefreshTokenDto:
        refresh_url_dto = RefreshTokenDto(
            client_id=self._config.client_id,
            client_secret=self._config.client_secret,
            refresh_token=refresh_token,
            grant_type="refresh_token",
        )
        return refresh_url_dto

    def _create_revoke_token_url(self, access_token: str) -> str:
        revoke_url_dto = RevokeTokenUrlDto(token=access_token)
        return append_query_params_to_url(GoogleOAuthEndpointEnum.revoke_endpoint, revoke_url_dto.as_dict())

    async def fetch_access_token(self, redirect_uri: str, code: str) -> GoogleOAuthResponseTokenSchema:
        access_token_data = self._create_access_token_data(redirect_uri, code)
        try:
            response = await self._http_client.post(
                GoogleOAuthEndpointEnum.token_endpoint,
                data=access_token_data.as_dict(),
            )
            response_token = GoogleOAuthResponseTokenSchema(**response)
        except (ValidationError, ClientErrorException) as error:
            logger.error(f"Can't fetch token from oauth google. Error={error}")
            raise OAuthRequestError("Some error from fetch token")
        return response_token

    async def fetch_user_info(self, google_access_info: GoogleOAuthResponseTokenSchema) -> OAuthUserInfoDto:
        try:
            user_jwt_decoded = jwt.decode(google_access_info.id_token, options={"verify_signature": False})
            user_info = GoogleOAuthResponseUserInfoSchema(**user_jwt_decoded)
        except (ValidationError, ClientErrorException, KeyError, TypeError, IndexError) as error:
            logger.error(f"Can't get user info from oauth google. Error={error}")
            raise OAuthRequestError("Some error from get user info")
        return OAuthUserInfoDto.from_google_response(user_info)

    async def add_access_token_to_cache(self, user_id: UUID, access_token: str, expires_in: int) -> None:
        cache_key = self._config.access_token_cache_key.format(user_id=user_id)
        await self._cache_client.put_to_cache(cache_key, access_token, expire=expires_in)
        logger.info(f"Google oauth access token has been added to cache: {cache_key}: {access_token}: {expires_in}")

    async def add_refresh_token_to_cache(self, user_id: UUID, refresh_token: str, expires_in: int) -> None:
        cache_key = self._config.refresh_token_cache_key.format(user_id=user_id)
        await self._cache_client.put_to_cache(cache_key, refresh_token, expire=expires_in)
        logger.info(f"Google oauth refresh token has been added to cache: {cache_key}: {refresh_token}: {expires_in}")

    async def set_refresh_token_cache_expire(self, user_id: UUID, expires_in: int) -> None:
        cache_key = self._config.refresh_token_cache_key.format(user_id=user_id)
        await self._cache_client.set_expire(cache_key, expire=expires_in)
        logger.info(f"Updated expire cache for Google oauth refresh token: {cache_key}: {expires_in}")

    async def remove_access_token_from_cache(self, user_id: UUID) -> None:
        cache_key = self._config.access_token_cache_key.format(user_id=user_id)
        await self._cache_client.del_from_cache(cache_key)
        logger.info(f"Google oauth access token has been removed from cache: {cache_key}")

    async def remove_refresh_token_from_cache(self, user_id: UUID) -> None:
        cache_key = self._config.refresh_token_cache_key.format(user_id=user_id)
        await self._cache_client.del_from_cache(cache_key)
        logger.info(f"Google oauth refresh token has been removed from cache: {cache_key}")

    async def revoke_token(self, user_id: UUID) -> None:
        cache_key = self._config.access_token_cache_key.format(user_id=user_id)
        access_token = await self._cache_client.get_from_cache(cache_key)
        if not access_token:
            raise OAuthTokenExpiredException
        try:
            revoke_token_url = self._create_revoke_token_url(access_token)
            await self._http_client.post(revoke_token_url)
        except ClientErrorException as error:
            logger.error(f"Can't revoke oauth google token. Error={error}")
            raise OAuthRequestError("Some error while was revoking the token")
        logger.info("Google oauth access token has been revoked")

    async def refresh_token(self, user_id: UUID) -> GoogleOAuthResponseRefreshSchema:
        cache_key = self._config.refresh_token_cache_key.format(user_id=user_id)
        refresh_token = await self._cache_client.get_from_cache(cache_key)
        if not refresh_token:
            raise OAuthTokenExpiredException
        try:
            refresh_token_data = self._create_refresh_token_data(refresh_token)
            response = await self._http_client.post(
                GoogleOAuthEndpointEnum.refresh_endpoint,
                data=refresh_token_data.as_dict(),
            )
            response_refresh = GoogleOAuthResponseRefreshSchema(**response)
        except (ValidationError, ClientErrorException) as error:
            logger.error(f"Can't refresh oauth google token. Error={error}")
            raise OAuthRequestError("Some error while was refreshing the token")
        return response_refresh

    async def _get_access_token_from_cache(self, user_id: UUID) -> str | None:
        access_cache_key = self._config.access_token_cache_key.format(user_id=user_id)
        return await self._cache_client.get_from_cache(access_cache_key)

    async def _get_refresh_token_from_cache(self, user_id: UUID) -> str | None:
        access_cache_key = self._config.refresh_token_cache_key.format(user_id=user_id)
        return await self._cache_client.get_from_cache(access_cache_key)

    async def get_tokens_pair(self, user_id: UUID) -> GoogleOAuthPairTokensResponseSchema:
        access_token = await self._get_access_token_from_cache(user_id)
        refresh_token = await self._get_refresh_token_from_cache(user_id)
        if not access_token or not refresh_token:
            raise OAuthTokenExpiredException
        return GoogleOAuthPairTokensResponseSchema(access_token=access_token, refresh_token=refresh_token)
