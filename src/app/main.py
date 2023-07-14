from logging import config as logging_config

import uvicorn
from api.routers.main import setup_routers
from common.exceptions.auth import OAuthException
from core.config import Settings
from core.logger import LOGGING
from dependencies.main import setup_dependencies
from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse
from middleware.main import setup_middleware
from providers.main import setup_providers
from telemetry.main import setup_telemetry

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


def create_app(settings: Settings):
    app = FastAPI(
        title=settings.project.name,
        docs_url='/docs',
        openapi_url='/api/openapi.json',
        default_response_class=ORJSONResponse,
        description="Сервис авторизации пользователей",
        version="1.0.0",
    )
    setup_providers(app, settings)
    setup_routers(app)
    setup_dependencies(app)
    setup_middleware(app)
    setup_telemetry(app, settings)
    return app


settings = Settings()
app = create_app(settings)


@app.exception_handler(OAuthException)
async def validation_exception_handler(request, exc):
    return ORJSONResponse({'detail': str(exc)}, status_code=status.HTTP_403_FORBIDDEN)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',  # noqa
        port=8001,
        reload=True,
    )
