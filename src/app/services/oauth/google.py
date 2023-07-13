import logging
from abc import ABC, abstractmethod
import jwt

from wrappers.cache.base import CacheServiceABC

from core.oauth_config import GoogleOAuthConfig
from services.oauth.enums import GoogleOAuthEndpointEnum
from wrappers.http import AsyncHTTPClientABC
from utils.common import append_query_params_to_url

from domain.oauth.google.dto import AuthorizationUrlDto, AccessTokenUrlDto, UserInfoUrlDto
from domain.oauth.dto import OAuthUserInfoDto
from domain.oauth.google.response import GoogleOAuthResponseTokenSchema, GoogleOAuthResponseUserInfoSchema
from wrappers.http.exceptions import ClientErrorException
from pydantic import ValidationError
from common.exceptions.base import OAuthRequestError

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


class GoogleOAuthService(GoogleOAuthServiceABC):
    def __init__(
        self,
        cache_client: CacheServiceABC,
        http_client: AsyncHTTPClientABC,
        config: GoogleOAuthConfig,
    ) -> None:
        self.config = config
        self.cache_client = cache_client
        self.http_client = http_client

    def create_authorization_url(self, redirect_uri: str) -> str:
        auth_url_dto = AuthorizationUrlDto(
            response_type="code",
            client_id=self.config.client_id,
            redirect_uri=redirect_uri,
            scope="openid email",
            access_type="offline"
        )
        return append_query_params_to_url(GoogleOAuthEndpointEnum.authorization_endpoint, auth_url_dto.as_dict())

    def _create_access_token_data(self, redirect_uri: str, code: str) -> AccessTokenUrlDto:

        access_url_dto = AccessTokenUrlDto(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            redirect_uri=redirect_uri,
            code=code,
            grant_type="authorization_code",
        )
        return access_url_dto

    async def fetch_access_token(self, redirect_uri: str, code: str) -> GoogleOAuthResponseTokenSchema:
        access_token_data = self._create_access_token_data(redirect_uri, code)
        try:
            response = await self.http_client.post(GoogleOAuthEndpointEnum.token_endpoint, data=access_token_data.as_dict())
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
