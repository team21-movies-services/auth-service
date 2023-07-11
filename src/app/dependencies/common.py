from fastapi import FastAPI, Request, Depends

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from core.config import Settings
from utils.rate_limit import RateLimiter
from wrappers.cache import RedisCacheService


async def get_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    app: FastAPI = request.app
    session_maker = app.state.async_session_maker
    session = session_maker()
    try:
        yield session
    finally:
        await session.close()


async def get_redis_client(
    request: Request,
) -> AsyncGenerator[Redis, None]:
    app: FastAPI = request.app
    redis_client: Redis = app.state.async_redis_client
    try:
        yield redis_client
    finally:
        await redis_client.close()


async def get_httpx_client(
    request: Request,
):
    app: FastAPI = request.app
    http_client: Redis = app.state.async_http_client
    yield http_client


def get_settings():
    return Settings()


def get_rate_limit(
    request: Request,
    settings: Settings = Depends(get_settings),
    redis_client: Redis = Depends(get_redis_client),
):
    client_host = request.client.host  # type: ignore
    cache_client = RedisCacheService(redis_client)

    return RateLimiter(
        max_requests=settings.project.rate_limit.rate_limit_max_request,
        period=settings.project.rate_limit.rate_limit_period,
        cache_client=cache_client,
        client_id=client_host,
    )
