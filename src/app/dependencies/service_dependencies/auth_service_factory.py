from fastapi import Depends
from redis.asyncio import Redis

from core.config import Settings
from dependencies.common import get_redis_client, get_settings
from dependencies.registrator import add_factory_to_mapper
from services.auth import AuthService, AuthServiceABC
from wrappers.cache.redis import RedisCacheService


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
