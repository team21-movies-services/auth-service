import logging

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from middleware.error import error_middleware
from middleware.request_id import RequestIdHeaderMiddleware
from middleware.trace import TracerRequestIdMiddleware

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex='.*',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestIdHeaderMiddleware)
    app.add_middleware(TracerRequestIdMiddleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=error_middleware)
