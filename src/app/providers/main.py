import logging
from fastapi import FastAPI

from core.config import Settings

from providers.pg_providers import SQLAlchemyProvider
from providers.cache_providers import RedisProvider

logger = logging.getLogger(__name__)


def setup_providers(app: FastAPI, settings: Settings):
    sa_provider = SQLAlchemyProvider(
        app=app,
        async_dns=settings.postgres.database_url,
        echo_log=settings.postgres.echo_log,
    )
    sa_provider.register_events()

    logger.info(f"Setup SQLAlchemy Provider. DSN: {settings.postgres.database_url}")

    redis_provider = RedisProvider(
        app=app,
        host=settings.redis.host,
        port=settings.redis.port,
    )
    redis_provider.register_events()

    logger.info(f"Setup Redis Provider. host:port: {settings.redis.host}:{settings.redis.port}")
