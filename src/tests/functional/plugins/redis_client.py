import pytest_asyncio
from redis.asyncio import Redis

from functional.settings import Settings


@pytest_asyncio.fixture(scope="session")
async def redis_client(settings: Settings):
    """Клиент для redis."""
    client: Redis = Redis(host=settings.redis.host, port=settings.redis.port)
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="class")
async def flushall_redis_data(redis_client: Redis):
    """Сброс кеша редиса."""
    await redis_client.flushall()
