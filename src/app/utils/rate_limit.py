import logging
from typing import Optional

from common.enums import RateLimitPeriodEnum
from common.exceptions.base import TooManyRequests
from wrappers.cache.base import CacheServiceABC

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(
        self,
        cache_client: CacheServiceABC,
        client_id: str,
        max_requests: int,
        period: RateLimitPeriodEnum,
    ) -> None:
        self.cache_client = cache_client
        self.client_id = client_id
        self.max_requests = max_requests
        self.period = period

    def _expire_from_period(self, period: RateLimitPeriodEnum) -> int:
        second = 1
        if period == RateLimitPeriodEnum.seconds:
            return second

        if period == RateLimitPeriodEnum.minutes:
            return second * 60

        if period == RateLimitPeriodEnum.hours:
            return second * 60 * 60

        return second

    async def check_limit(
        self,
        resource: str,
        max_requests: Optional[int] = None,
        period: Optional[RateLimitPeriodEnum] = None,
    ) -> None:
        rate_limit_key = f"rate_limit:{resource}_{self.client_id}"
        max_requests = max_requests or self.max_requests

        current_usage = await self.cache_client.get_from_cache(rate_limit_key)
        logger.info(
            f"Get from cache '{rate_limit_key}' for check rate limit. " f"Max Limit = {max_requests}",
        )
        if current_usage:
            logger.info(f"Get count requests: {current_usage}")
            if int(current_usage) >= max_requests:
                raise TooManyRequests

        expire = self._expire_from_period(period or self.period)
        await self.cache_client.increment(rate_limit_key)
        await self.cache_client.set_expire(rate_limit_key, expire)
        logger.info(f"Set '{rate_limit_key}' to cache with expire {expire}")
