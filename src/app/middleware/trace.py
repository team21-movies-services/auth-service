from opentelemetry.trace import get_current_span
from starlette.middleware.base import BaseHTTPMiddleware


class TracerRequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        request_id = request.headers.get('X-Request-Id')
        if request_id:
            span = get_current_span()
            span.set_attribute('http.request_id', request_id)

        return response
