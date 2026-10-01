"""Lightweight OpenTelemetry helpers for agent workloads.

This module intentionally keeps instrumentation in the authoring-time code path instead of
assuming a post-deploy patch step. It also stays importable when optional OTel or Azure Monitor
packages are not installed, which keeps offline labs and unit tests friction-free.
"""
from __future__ import annotations

import inspect
import os
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Iterator

try:  # pragma: no cover - import availability depends on learner environment
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import Status, StatusCode
except ImportError:  # pragma: no cover - graceful offline fallback
    trace = None
    Resource = None
    TracerProvider = None
    BatchSpanProcessor = None
    Status = None
    StatusCode = None

try:  # pragma: no cover - optional dependency by design
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
except ImportError:  # pragma: no cover - graceful offline fallback
    AzureMonitorTraceExporter = None

_IS_CONFIGURED = False
_TRACER = None


def configure_otel(
    service_name: str = "foundry-agent",
    connection_string: str | None = None,
) -> bool:
    """Configure a tracer provider and optional Azure Monitor exporter.

    Returns:
        ``True`` when an Azure Monitor exporter was attached, otherwise ``False``.
        Returning ``False`` is not an error; it simply means the module is running offline or
        without the optional exporter package.
    """
    global _IS_CONFIGURED, _TRACER

    if trace is None or Resource is None or TracerProvider is None:
        _IS_CONFIGURED = False
        _TRACER = None
        return False

    if _TRACER is not None:
        return bool(connection_string or os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"))

    resolved_service_name = os.getenv("OTEL_SERVICE_NAME", service_name)
    provider = TracerProvider(resource=Resource.create({"service.name": resolved_service_name}))

    resolved_connection_string = (connection_string or os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")).strip()
    exporter_enabled = False

    if resolved_connection_string and AzureMonitorTraceExporter is not None and BatchSpanProcessor is not None:
        try:
            exporter = AzureMonitorTraceExporter(connection_string=resolved_connection_string)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            exporter_enabled = True
        except Exception:
            exporter_enabled = False

    trace.set_tracer_provider(provider)
    _TRACER = trace.get_tracer(__name__)
    _IS_CONFIGURED = True
    return exporter_enabled


def _get_tracer():
    if _TRACER is None and not _IS_CONFIGURED:
        configure_otel()
    return _TRACER


@contextmanager
def _start_span(span_name: str, **attributes: Any) -> Iterator[Any]:
    """Start a span when OTel is available, otherwise degrade to a no-op."""
    tracer = _get_tracer()
    if tracer is None:
        yield None
        return

    with tracer.start_as_current_span(span_name) as span:
        for key, value in attributes.items():
            if value is not None:
                span.set_attribute(key, value)
        yield span


@contextmanager
def start_agent_run_span(name: str, **attributes: Any) -> Iterator[Any]:
    """Start a root span for one agent run."""
    with _start_span(f"agent.run:{name}", **attributes) as span:
        yield span


def instrument_tool_call(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap a tool function in a child span.

    The decorator supports both synchronous and asynchronous callables so the same pattern works
    across simple helper functions and async SDK/tool invocations.
    """

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with _start_span(
                f"tool.call:{func.__name__}",
                tool_name=func.__name__,
                tool_call_style="async",
                tool_argument_count=len(args) + len(kwargs),
            ) as span:
                try:
                    result = await func(*args, **kwargs)
                    if span is not None:
                        span.set_attribute("tool.result_type", type(result).__name__)
                        span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as exc:
                    if span is not None:
                        span.record_exception(exc)
                        span.set_status(Status(StatusCode.ERROR, str(exc)))
                    raise

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        with _start_span(
            f"tool.call:{func.__name__}",
            tool_name=func.__name__,
            tool_call_style="sync",
            tool_argument_count=len(args) + len(kwargs),
        ) as span:
            try:
                result = func(*args, **kwargs)
                if span is not None:
                    span.set_attribute("tool.result_type", type(result).__name__)
                    span.set_status(Status(StatusCode.OK))
                return result
            except Exception as exc:
                if span is not None:
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise

    return sync_wrapper
