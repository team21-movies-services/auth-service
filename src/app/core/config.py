import os

from common.enums import RateLimitPeriodEnum
from core.oauth_config import OAuthConfig
from pydantic import BaseSettings, Field


# Настройки Redis
class RedisConfig(BaseSettings):
    port: int = Field(default=6379, env='REDIS_PORT')
    host: str = Field(default='127.0.0.1', env='REDIS_HOST')


class TraceConfig(BaseSettings):
    jaeger_port: int = Field(default=6831, env='JAEGER_UDP_PORT')
    jaeger_host: str = Field(default='127.0.0.1', env='JAEGER_HOST')
    debug_trace: bool = Field(default=False, env='DEBUG_TRACE')
    enable_trace: bool = Field(default=True, env='ENABLE_TRACE')


# Настройки Postgres
class PostgresConfig(BaseSettings):
    echo_log: bool = Field(default=False, env='DB_ECHO_LOG')
    host: str = Field(default='127.0.0.1', env='SQL_HOST')
    port: int = Field(default=5432, env='SQL_PORT')
    database: str = Field(default='auth_database', env='SQL_DATABASE')
    user: str = Field(default='user1', env='SQL_USER')
    password: str = Field(default='qwerty123', env='SQL_PASSWORD')

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def migration_database_url(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RateLimitConfig(BaseSettings):
    rate_limit_max_request: int = Field(default=100, env='RATE_LIMIT_MAX_REQUEST')
    # FIXME: не устанавливается из env...
    rate_limit_period: RateLimitPeriodEnum = Field(default=RateLimitPeriodEnum, env='RATE_LIMIT_PERIOD')


# Название проекта. Используется в Swagger-документации
class ProjectConfig(BaseSettings):
    name: str = Field(default='auth_api', env='PROJECT_NAME')
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    jwt_secret_key: str = Field(default=..., env='JWT_SECRET_KEY')
    rate_limit: RateLimitConfig = RateLimitConfig()


class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()
    redis: RedisConfig = RedisConfig()
    postgres: PostgresConfig = PostgresConfig()
    oauth: OAuthConfig = OAuthConfig()
    tracer: TraceConfig = TraceConfig()


settings = Settings()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
