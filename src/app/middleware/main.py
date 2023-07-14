import logging

from fastapi import FastAPI
from middleware.error import error_middleware
from middleware.request_id import RequestIdHeaderMiddleware
from middleware.trace import TracerRequestIdMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI):
    app.add_middleware(RequestIdHeaderMiddleware)
    app.add_middleware(TracerRequestIdMiddleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=error_middleware)
