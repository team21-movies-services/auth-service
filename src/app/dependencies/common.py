from fastapi import FastAPI, Request

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from core.config import Settings


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


def get_settings():
    return Settings()
