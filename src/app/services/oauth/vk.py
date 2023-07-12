import logging

from wrappers.cache.base import CacheServiceABC

from core.oauth_config import VKOAuthConfig
from services.oauth.enums import VKOAuthEndpointEnum
from wrappers.http import AsyncHTTPClientABC
from utils.common import append_query_params_to_url

from domain.oauth.vk.dto import AuthorizationUrlDto, AccessTokenUrlDto
from domain.oauth.vk.response import OAuthResponseTokenSchema

logger = logging.getLogger(__name__)


class VKOAuthServiceABC:

    def create_authorization_url(self, redirect_uri: str) -> str:
        ...

    async def fetch_access_token(self, redirect_uri: str, code: str) -> OAuthResponseTokenSchema:
        ...


class VKOAuthService:
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

    def _create_access_token_url(self, redirect_uri: str, code: str) -> str:

        access_url_dto = AccessTokenUrlDto(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            redirect_uri=redirect_uri,
            code=code,
        )
        return append_query_params_to_url(VKOAuthEndpointEnum.token_endpoint, access_url_dto.as_dict())

    async def fetch_access_token(self, redirect_uri: str, code: str) -> OAuthResponseTokenSchema:
        get_access_token_url = self._create_access_token_url(redirect_uri, code)
        response = await self.http_client.get(get_access_token_url)
        response_token = OAuthResponseTokenSchema(**response)
        print(response_token)
        return response_token

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
