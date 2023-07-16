import logging
from abc import ABC, abstractmethod

from pydantic import ValidationError

from common.exceptions.base import OAuthRequestError
from core.oauth_config import VKOAuthConfig
from domain.oauth.dto import OAuthUserInfoDto
from domain.oauth.vk.dto import AccessTokenUrlDto, AuthorizationUrlDto, UserInfoUrlDto
from domain.oauth.vk.response import (
    VKOAuthResponseTokenSchema,
    VKOAuthResponseUserInfoSchema,
)
from services.oauth.enums import VKOAuthEndpointEnum
from utils.common import append_query_params_to_url
from wrappers.cache.base import CacheServiceABC
from wrappers.http import AsyncHTTPClientABC
from wrappers.http.exceptions import ClientErrorException

logger = logging.getLogger(__name__)


class VKOAuthServiceABC(ABC):
    @abstractmethod
    def create_authorization_url(self, redirect_uri: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def fetch_access_token(self, redirect_uri: str, code: str) -> VKOAuthResponseTokenSchema:
        raise NotImplementedError

    @abstractmethod
    async def fetch_user_info(self, vk_access_info: VKOAuthResponseTokenSchema) -> OAuthUserInfoDto:
        raise NotImplementedError


class VKOAuthService(VKOAuthServiceABC):
    def __init__(
        self,
        cache_client: CacheServiceABC,
        http_client: AsyncHTTPClientABC,
        config: VKOAuthConfig,
    ) -> None:
        self.config = config
        self.cache_client = cache_client
        self.http_client = http_client

    def create_authorization_url(self, redirect_uri: str) -> str:
        auth_url_dto = AuthorizationUrlDto(
            response_type="code",
            client_id=self.config.client_id,
            redirect_uri=redirect_uri,
            scope="email",
            display="page",
        )
        return append_query_params_to_url(VKOAuthEndpointEnum.authorization_endpoint, auth_url_dto.as_dict())

    def _create_access_token_url(self, redirect_uri: str, code: str) -> str:
        access_url_dto = AccessTokenUrlDto(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            redirect_uri=redirect_uri,
            code=code,
        )
        return append_query_params_to_url(VKOAuthEndpointEnum.token_endpoint, access_url_dto.as_dict())

    def _create_user_info_url(self, access_token: str, user_id: int) -> str:
        user_url_dto = UserInfoUrlDto(access_token=access_token, user_ids=user_id)
        return append_query_params_to_url(VKOAuthEndpointEnum.user_info, user_url_dto.as_dict())

    async def fetch_access_token(self, redirect_uri: str, code: str) -> VKOAuthResponseTokenSchema:
        get_access_token_url = self._create_access_token_url(redirect_uri, code)
        try:
            response = await self.http_client.get(get_access_token_url)
            response_token = VKOAuthResponseTokenSchema(**response)
        except (ValidationError, ClientErrorException) as error:
            logger.error(f"Can't fetch token from oauth vk. Error={error}")
            raise OAuthRequestError("Some error from fetch token")
        return response_token

    async def fetch_user_info(self, vk_access_info: VKOAuthResponseTokenSchema) -> OAuthUserInfoDto:
        get_user_info_url = self._create_user_info_url(vk_access_info.access_token, vk_access_info.user_id)
        try:
            response = await self.http_client.get(get_user_info_url)
            user_info = VKOAuthResponseUserInfoSchema(**response["response"][0], email=vk_access_info.email)
        except (ValidationError, ClientErrorException, KeyError, TypeError, IndexError) as error:
            logger.error(f"Can't get user info from oauth vk. Error={error}")
            raise OAuthRequestError("Some error from get user info")
        return OAuthUserInfoDto.from_vk_response(user_info)
