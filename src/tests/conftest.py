import pytest
import asyncio

from functional.settings import get_settings

pytest_plugins = (
    "functional.plugins.api_client",
    "functional.plugins.redis_client",
    "functional.plugins.auth_service",
    "functional.plugins.role_service",
    "functional.plugins.user_service",
    "functional.plugins.history_service",
    "functional.testdata.users",
    "functional.testdata.roles",
    "functional.testdata.device",
)


@pytest.fixture(scope="session")
def settings():
    """Получение настроек для тестов."""
    return get_settings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
