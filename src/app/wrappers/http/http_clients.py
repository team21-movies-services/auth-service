import logging
from typing import Optional, Any

from wrappers.http.base import AsyncHTTPClientABC
from wrappers.http.exceptions import ClientErrorException

from httpx import AsyncClient, codes


logger = logging.getLogger(__name__)


class AsyncHTTPClient(AsyncHTTPClientABC):
    def __init__(self, httpx_client: AsyncClient):
        self.httpx_client = httpx_client

    async def _request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> Any:
        response = await self.httpx_client.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data,
        )
        if response.status_code != codes.OK:
            raise ClientErrorException(f"Error send post request. detail={response.content!r}")
        return response.json()

    async def get(
        self,
        path: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Any:
        return await self._request(
            method="GET",
            url=path,
            headers=headers,
            params=params,
        )

    async def post(
        self,
        path: str,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        return await self._request(
            method="POST",
            url=path,
            headers=headers,
            data=data,
            params=params,
        )
