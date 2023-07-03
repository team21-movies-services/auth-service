from functools import lru_cache
from pydantic import BaseSettings, Field


class TestRedisConfig(BaseSettings):
    host: str = Field(default='localhost', env='REDIS_HOST')
    port: int = Field(default=16379, env='REDIS_PORT')


# Настройки Postgres
class TestPostgresConfig(BaseSettings):
    echo_log: bool = Field(default=False, env='DB_ECHO_LOG')
    host: str = Field(default='127.0.0.1', env='SQL_HOST')
    port: int = Field(default=5432, env='SQL_PORT')
    database: str = Field(default='test_db', env='SQL_DATABASE')
    user: str = Field(default='test_user', env='SQL_USER')
    password: str = Field(default='test_password', env='SQL_PASSWORD')

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class TestProjectConfig(BaseSettings):
    host: str = Field(default='localhost', env='PROJECT_HOST')
    port: int = Field(default=18001, env='PROJECT_PORT')
    jwt_secret: str = 'asdnjklnjkl123412bjk4bjk'


class Settings(BaseSettings):
    redis: TestRedisConfig = TestRedisConfig()
    project: TestProjectConfig = TestProjectConfig()
    postgres: TestPostgresConfig = TestPostgresConfig()


@lru_cache
def get_settings() -> Settings:
    return Settings()
