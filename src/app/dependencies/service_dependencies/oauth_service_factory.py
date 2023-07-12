from fastapi import Depends
from redis.asyncio import Redis
from httpx import AsyncClient

from dependencies.registrator import add_factory_to_mapper
from services.oauth import YandexOAuthService, YandexOAuthServiceABC, VKOAuthServiceABC, VKOAuthService

from core.config import Settings

from dependencies.common import get_settings, get_redis_client, get_httpx_client
from wrappers import AsyncHTTPClient, RedisCacheService


@add_factory_to_mapper(YandexOAuthServiceABC)
def create_yandex_oauth_service(
    settings: Settings = Depends(get_settings),
    redis_client: Redis = Depends(get_redis_client),
    httpx_client: AsyncClient = Depends(get_httpx_client),
) -> YandexOAuthService:
    cache_client = RedisCacheService(redis_client)
    http_client = AsyncHTTPClient(httpx_client=httpx_client)
    return YandexOAuthService(
        cache_client=cache_client,
        config=settings.oauth.yandex,
        http_client=http_client,
    )


@add_factory_to_mapper(VKOAuthServiceABC)
def create_vk_oauth_service(
    settings: Settings = Depends(get_settings),
    redis_client: Redis = Depends(get_redis_client),
    httpx_client: AsyncClient = Depends(get_httpx_client),
) -> VKOAuthService:
    cache_client = RedisCacheService(redis_client)
    http_client = AsyncHTTPClient(httpx_client=httpx_client)
    return VKOAuthService(
        cache_client=cache_client,
        config=settings.oauth.vk,
        http_client=http_client,
    )
