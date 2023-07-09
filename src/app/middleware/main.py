import logging
from fastapi import FastAPI

from middleware.request_id import RequestIdHeaderMiddleware

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI):
    app.add_middleware(RequestIdHeaderMiddleware)
