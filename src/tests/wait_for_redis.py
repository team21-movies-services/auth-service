import logging
import sys

import backoff
from pydantic.env_settings import BaseSettings
from pydantic.fields import Field
from redis import Redis
from redis.exceptions import ConnectionError

BACKOFF_CONFIG = {
    "wait_gen": backoff.expo,
    "exception": Exception,
    "jitter": None,
    "max_value": 20,
}

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestRedisConfig(BaseSettings):
    host: str = Field(default='localhost', env='REDIS_HOST')
    port: int = Field(default=16379, env='REDIS_PORT')


@backoff.on_exception(**BACKOFF_CONFIG, logger=logger)
def ping_redis():
    client = Redis(host=config.host, port=config.port)
    if not client.ping():
        raise ConnectionError


if __name__ == "__main__":
    config = TestRedisConfig()
    ping_redis()
