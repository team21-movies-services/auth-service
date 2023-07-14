from typing import Union

from redis.asyncio import Redis
from wrappers.cache.base import CacheServiceABC


class RedisCacheService(CacheServiceABC):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get_from_cache(self, key: str, **kwargs) -> str | None:
        value = await self.redis.get(key)
        if value:
            return value.decode()  # type: ignore
        return None

    async def del_from_cache(self, key: str, **kwargs) -> None:
        await self.redis.delete(key)
        return None

    async def put_to_cache(
        self,
        key: str,
        value: Union[str, bytes],
        expire: int,
        **kwargs,
    ) -> None:
        await self.redis.set(key, value, expire)

    async def increment(self, key: str, amount: int = 1) -> int:
        return await self.redis.incr(key, amount=amount)

    async def set_expire(self, key: str, expire: int = 1) -> int:
        return await self.redis.expire(key, expire)
