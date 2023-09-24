import pytest_asyncio
from functional.settings import Settings

from models import AuthUser
from services.auth import AuthService
from wrappers.cache.redis import RedisCacheService


@pytest_asyncio.fixture(scope='session')
async def auth_service(settings: Settings, redis_client):
    yield AuthService(cache_client=RedisCacheService(redis_client), jwt_secret_key=settings.project.jwt_secret)


@pytest_asyncio.fixture()
async def auth_tokens(auth_user: AuthUser, auth_service: AuthService, flushall_redis_data):
    tokens = await auth_service.create_token_pair(auth_user.id, is_superuser=auth_user.is_superuser, roles=[])
    return tokens.dict()


@pytest_asyncio.fixture()
async def admin_auth_token(auth_admin_user, auth_service: AuthService, flushall_redis_data):
    tokens = await auth_service.create_token_pair(
        auth_admin_user.id, is_superuser=auth_admin_user.is_superuser, roles=[]
    )
    return tokens.dict()
