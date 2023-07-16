from fastapi import Depends
from httpx import AsyncClient
from redis.asyncio import Redis

from core.config import Settings
from dependencies.common import get_httpx_client, get_redis_client, get_settings
from dependencies.registrator import add_factory_to_mapper
from services import oauth
from wrappers import AsyncHTTPClient, RedisCacheService


@add_factory_to_mapper(oauth.YandexOAuthServiceABC)
def create_yandex_oauth_service(
    settings: Settings = Depends(get_settings),
    redis_client: Redis = Depends(get_redis_client),
    httpx_client: AsyncClient = Depends(get_httpx_client),
) -> oauth.YandexOAuthService:
    cache_client = RedisCacheService(redis_client)
    http_client = AsyncHTTPClient(httpx_client=httpx_client)
    return oauth.YandexOAuthService(
        cache_client=cache_client,
        config=settings.oauth.yandex,
        http_client=http_client,
    )


@add_factory_to_mapper(oauth.VKOAuthServiceABC)
def create_vk_oauth_service(
    settings: Settings = Depends(get_settings),
    redis_client: Redis = Depends(get_redis_client),
    httpx_client: AsyncClient = Depends(get_httpx_client),
) -> oauth.VKOAuthService:
    cache_client = RedisCacheService(redis_client)
    http_client = AsyncHTTPClient(httpx_client=httpx_client)
    return oauth.VKOAuthService(
        cache_client=cache_client,
        config=settings.oauth.vk,
        http_client=http_client,
    )


@add_factory_to_mapper(oauth.GoogleOAuthServiceABC)
def create_google_oauth_service(
    settings: Settings = Depends(get_settings),
    redis_client: Redis = Depends(get_redis_client),
    httpx_client: AsyncClient = Depends(get_httpx_client),
) -> oauth.GoogleOAuthService:
    cache_client = RedisCacheService(redis_client)
    http_client = AsyncHTTPClient(httpx_client=httpx_client)
    return oauth.GoogleOAuthService(
        cache_client=cache_client,
        config=settings.oauth.google,
        http_client=http_client,
    )
