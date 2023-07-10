from fastapi import Request, Response, status
from starlette.responses import JSONResponse
from typing import Callable, Awaitable

from common.exceptions.base import TooManyRequests


async def error_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    status_code = status.HTTP_200_OK
    content = {}

    try:
        response = await call_next(request)
        return response
    except TooManyRequests:
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
        content['message'] = 'too many requests. Try later'

    content['code'] = str(status_code)
    return JSONResponse(status_code=status_code, content=content)
