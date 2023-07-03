import logging
from typing import Any

import httpx
from fastapi import Depends
from httpx import Response
from redis.asyncio import Redis

import common.exceptions.auth as auth_exceptions
from cache.redis import RedisCacheService
from core.config import Settings
from dependencies.common import get_settings, get_redis_client
from schemas.oauth import OAuthTokens, OAuthTokensError, ResponseStatus, OAuthUserInfoSchema

logger = logging.getLogger(__name__)


class YandexOAuthService:
    authorization_endpoint = 'https://oauth.yandex.ru/authorize'
    token_endpoint = 'https://oauth.yandex.ru/token'
    token_revoke = 'https://oauth.yandex.ru/revoke_token'
    userinfo = 'https://login.yandex.ru/info'
    userinfo_converter = OAuthUserInfoSchema.from_yandex

    def create_authorization_url(self, **kwargs):
        url = (
            f"https://oauth.yandex.ru/authorize?response_type=code"
            f"&client_id={self.config.client_id}"
        )
        for key in kwargs:
            if key not in self.config.valid_keys:
                continue
            url += f'&{key}={kwargs[key]}'
        return url

    def __init__(self, settings: Settings = Depends(get_settings),
                 redis_client: Redis = Depends(get_redis_client)):
        self.config = settings.oauth.yandex
        self.cache_client = RedisCacheService(redis_client)

    async def _post_request(self, url: str, response_schema: Any = OAuthTokens, **kwargs):
        async with httpx.AsyncClient() as client:
            r: Response = await client.post(url, data={
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                **kwargs,
            })
            if r.status_code == httpx.codes.OK:
                return response_schema(**r.json())

            err = OAuthTokensError(**r.json())
            logger.error(f'Request to token: {kwargs}. Error: {err.log_error()}')
            raise auth_exceptions.OAuthException(err.log_error())

    async def fetch_token(self, code: str, state: str = None):
        return await self._post_request(url=self.token_endpoint,
                                        grant_type='authorization_code',
                                        code=code)

    async def refresh_tokens(self, refresh_token):
        return await self._post_request(url=self.token_endpoint,
                                        grant_type='refresh_token',
                                        refresh_token=refresh_token)

    async def revoke_token(self, user_id) -> ResponseStatus:
        access_token = await self.cache_client.get_from_cache(f'oauth-{user_id}')
        if not access_token:
            logger.info('OAuth access token already expire. user_id - {user_id}')
            return ResponseStatus(status='ok')
        return await self._post_request(url=self.token_revoke,
                                        response_schema=ResponseStatus,
                                        access_token=access_token)

    async def add_access_token_to_cache(self, user_id, tokens: OAuthTokens):
        await self.cache_client.put_to_cache(f'oauth-{user_id}', tokens.access_token, expire=tokens.expires_in)

    async def user_info(self, access_token):
        async with httpx.AsyncClient() as client:
            r: Response = await client.get(self.userinfo, headers={
                'Authorization': f'OAuth {access_token}',
            })
            if r.status_code == httpx.codes.OK:
                return self.userinfo_converter(**r.json())
            logger.error(f'Request to userinfo: {r.status_code}. Error: {r.text}')
            raise auth_exceptions.OAuthException()
