from abc import ABC, abstractmethod
from typing import Union


class CacheServiceABC(ABC):
    @abstractmethod
    async def get_from_cache(self, key: str, **kwargs) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def del_from_cache(self, key: str, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def put_to_cache(
        self,
        key: str,
        value: Union[str, bytes],
        expire: int,
        **kwargs,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        raise NotImplementedError

    @abstractmethod
    async def set_expire(self, key: str, expire: int = 1) -> int:
        raise NotImplementedError
