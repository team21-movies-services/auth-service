from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
import logging


logger = logging.getLogger(__name__)


def _get_exporter() -> ConsoleSpanExporter:
    return ConsoleSpanExporter()


def _get_span_processor(exporter: ConsoleSpanExporter) -> BatchSpanProcessor:
    return BatchSpanProcessor(exporter)


def setup_console(tracer: TracerProvider) -> None:
    exporter = _get_exporter()
    span_processor = _get_span_processor(exporter)
    tracer.add_span_processor(span_processor)
