import logging

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import Tracer, get_tracer, set_tracer_provider
from telemetry.console import setup_console
from telemetry.jaeger import setup_jaeger

from core.config import Settings, settings


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

    if settings.tracer.debug_trace:
        setup_console(tracer)
        logger.info("Setup Console Tracer")

    FastAPIInstrumentor.instrument_app(app)


def get_current_tracer() -> Tracer:
    return get_tracer(settings.project.name)
