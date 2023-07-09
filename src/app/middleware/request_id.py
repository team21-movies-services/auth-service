from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import ORJSONResponse
from fastapi import status


class RequestIdHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            content = {'detail': 'X-Request-Id is required'}
            return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)
        return response
