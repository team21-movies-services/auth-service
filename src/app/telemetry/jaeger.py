import logging

from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.config import Settings

logger = logging.getLogger(__name__)


def _get_exporter(settings: Settings):
    return JaegerExporter(agent_host_name=settings.tracer.jaeger_host, agent_port=settings.tracer.jaeger_port)


def _get_span_processor(exporter: JaegerExporter):
    return BatchSpanProcessor(exporter)


def setup_jaeger(tracer: TracerProvider, settings: Settings) -> None:
    exporter = _get_exporter(settings)
    span_processor = _get_span_processor(exporter)
    tracer.add_span_processor(span_processor)
