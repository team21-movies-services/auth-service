from fastapi import FastAPI
from opentelemetry.instrumentation.redis import RedisInstrumentor
from redis.asyncio import Redis

from common.exceptions import AppException
from providers import BaseProvider


class RedisProvider(BaseProvider):
    def __init__(
        self,
        app: FastAPI,
        host: str,
        port: int,
    ):
        self.app = app
        self.host = host
        self.port = port

    async def startup(self):
        """FastAPI startup event"""
        # TODO: backoff

        self.redis_client: Redis = Redis(host=self.host, port=self.port)

        if not await self.redis_client.ping():
            raise AppException()

        setattr(self.app.state, "async_redis_client", self.redis_client)

        RedisInstrumentor().instrument()

    async def shutdown(self):
        """FastAPI shutdown event"""
        if self.redis_client:
            await self.redis_client.close()
