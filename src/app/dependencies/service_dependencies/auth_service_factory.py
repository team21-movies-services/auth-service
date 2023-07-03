from fastapi import Depends

from dependencies.registrator import add_factory_to_mapper
from services.auth import AuthServiceABC, AuthService

from core.config import Settings

from dependencies.common import get_settings, get_redis_client
from redis.asyncio import Redis

from cache.redis import RedisCacheService


@add_factory_to_mapper(AuthServiceABC)
def create_auth_service(
    settings: Settings = Depends(get_settings),
    redis_client: Redis = Depends(get_redis_client),
):
    cache_client = RedisCacheService(redis_client)
    return AuthService(
        cache_client=cache_client,
        jwt_secret_key=settings.project.jwt_secret_key,
    )
