from typing import Optional, Any

from wrappers.http.base import AsyncHTTPClientABC

from httpx import AsyncClient


class AsyncHTTPClient(AsyncHTTPClientABC):

    def __init__(self, httpx_client: AsyncClient):
        self.httpx_client = httpx_client

    async def get(
        self,
        path: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Any:
        async with self.httpx_client as client:
            response = await client.get('https://ya.ru')
            print('\n\n')
            print(response.content)
            print('\n\n')

    async def post(
        self,
        path: str,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        async with self.httpx_client as client:
            response = await client.post('https://ya.ru')
            print('\n\n')
            print(response.content)
            print('\n\n')
