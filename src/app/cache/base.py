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
    async def put_to_cache(self, key: str, value: Union[str, bytes], expire: int, **kwargs) -> None:
        raise NotImplementedError
