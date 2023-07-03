import os

from pydantic import BaseSettings, Field

# Настройки Redis
from core.oauth_config import OAuthConfig


class RedisConfig(BaseSettings):
    port: int = Field(default=6379, env='REDIS_PORT')
    host: str = Field(default='127.0.0.1', env='REDIS_HOST')


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


# Название проекта. Используется в Swagger-документации
class ProjectConfig(BaseSettings):
    name: str = Field('auth_api', env='PROJECT_NAME')
    log_level: str = Field('INFO', env='LOG_LEVEL')
    jwt_secret_key: str = Field('asdnjklnjkl123412bjk4bjk', env='JWT_SECRET_KEY')


class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()
    redis: RedisConfig = RedisConfig()
    postgres: PostgresConfig = PostgresConfig()
    oauth: OAuthConfig = OAuthConfig()


settings = Settings()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
