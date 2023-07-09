from fastapi import FastAPI

from opentelemetry.trace import set_tracer_provider, get_tracer, Tracer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import logging
from core.config import Settings, settings
from telemetry.jaeger import setup_jaeger
from telemetry.console import setup_console


logger = logging.getLogger(__name__)


def _setup_tracer(settings: Settings) -> TracerProvider:
    resource = Resource.create(attributes={"service.name": settings.project.name})
    tracer = TracerProvider(resource=resource)
    set_tracer_provider(tracer)
    return tracer


def setup_telemetry(app: FastAPI, settings: Settings):

    tracer = _setup_tracer(settings)
    logger.info(f"Init main Tracer Provider - service name: {settings.project.name}")

    setup_jaeger(tracer, settings)
    logger.info(f"Setup Jaeger Tracer - host:port: {settings.tracer.jaeger_host}:{settings.tracer.jaeger_port}")

    setup_console(tracer)
    logger.info("Setup Console Tracer")

    FastAPIInstrumentor.instrument_app(app)


def get_current_tracer() -> Tracer:
    return get_tracer(settings.project.name)
