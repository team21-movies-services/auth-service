from abc import ABC, abstractmethod

from cache.base import CacheServiceABC


class RateLimitServiceABC(ABC):

    @abstractmethod
    def set_limit(self, limit_request: int, per: str) -> None:
        ...


class RateLimitService(RateLimitServiceABC):
    def __init__(self, cache_client: CacheServiceABC, jwt_secret_key: str) -> None:
        self.jwt_secret_key = jwt_secret_key
        self.cache_client = cache_client

    def set_limit(self, limit_request: int, per: str) -> None:
        ...
