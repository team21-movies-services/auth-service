import logging
from fastapi import FastAPI

from middleware.request_id import RequestIdHeaderMiddleware
from middleware.trace import TracerRequestIdMiddleware

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI):
    app.add_middleware(RequestIdHeaderMiddleware)
    app.add_middleware(TracerRequestIdMiddleware)
