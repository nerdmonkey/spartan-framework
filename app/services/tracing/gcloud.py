from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, Optional

from .base import BaseTracer


try:
    from opentelemetry import trace
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.semconv.resource import ResourceAttributes
    from opentelemetry.trace import Status, StatusCode

    try:
        from opentelemetry.resourcedetector.gcp_resource_detector import (
            GoogleCloudResourceDetector,
        )

        GCP_RESOURCE_DETECTOR_AVAILABLE = True
    except ImportError:
        GCP_RESOURCE_DETECTOR_AVAILABLE = False

    GCP_TRACING_AVAILABLE = True
except Exception as e:  # pragma: no cover - availability depends on env
    GCP_TRACING_AVAILABLE = False
    GCP_RESOURCE_DETECTOR_AVAILABLE = False
    _IMPORT_ERROR = e


class GCloudTracer(BaseTracer):
    """
    Google Cloud tracer using OpenTelemetry.

    Implements distributed tracing following GCP best practices:
    - Uses OpenTelemetry API for instrumentation
    - Exports traces to Google Cloud Trace
    - Supports context propagation
    - Includes resource detection for GCP services
    - Proper error handling and span status
    """

    def __init__(self, service_name: str, project_id: Optional[str] = None):
        if not GCP_TRACING_AVAILABLE:
            error_msg = "OpenTelemetry dependencies not available."
            if hasattr(globals(), "_IMPORT_ERROR"):
                error_msg += f" Error: {_IMPORT_ERROR}"
            else:
                error_msg += (
                    " Install with: pip install opentelemetry-api "
                    "opentelemetry-sdk opentelemetry-exporter-gcp-trace"
                )
            raise ImportError(error_msg)

        self.service_name = service_name
        self.project_id = project_id
        self._setup_tracer()

    def _setup_tracer(self):
        """Initialize OpenTelemetry tracer with Cloud Trace exporter."""
        # Create resource with service name and auto-detect GCP resources
        resource_attrs = {
            ResourceAttributes.SERVICE_NAME: self.service_name,
        }

        # Detect GCP resources if available
        if GCP_RESOURCE_DETECTOR_AVAILABLE:
            try:
                detector = GoogleCloudResourceDetector()
                detected_resource = detector.detect()
                resource = detected_resource.merge(Resource(resource_attrs))
            except Exception:
                # Fall back to basic resource if detection fails
                resource = Resource(resource_attrs)
        else:
            resource = Resource(resource_attrs)

        # Create TracerProvider with resource
        provider = TracerProvider(resource=resource)

        # Configure Cloud Trace exporter
        try:
            exporter = CloudTraceSpanExporter(project_id=self.project_id)
            # Use BatchSpanProcessor for better performance
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
        except Exception as e:
            # If exporter fails (e.g., no credentials), log but continue
            # This allows local development without GCP credentials
            import sys

            print(
                f"Warning: Failed to initialize Cloud Trace exporter: {e}",
                file=sys.stderr,
            )

        # Set as global tracer provider
        trace.set_tracer_provider(provider)

        # Get tracer instance
        self.tracer = trace.get_tracer(self.service_name)

    def capture_lambda_handler(self, func):
        """
        Decorator for tracing Lambda/Cloud Function handlers.
        Creates a span for the entire handler execution.
        """

        @wraps(func)
        def wrapper(event, context):
            with self.tracer.start_as_current_span(
                f"{func.__name__}",
                kind=trace.SpanKind.SERVER,
            ) as span:
                try:
                    # Add event attributes to span
                    if isinstance(event, dict):
                        for key, value in event.items():
                            if isinstance(value, (str, int, float, bool)):
                                span.set_attribute(f"event.{key}", value)

                    # Add context attributes if available
                    if hasattr(context, "request_id"):
                        span.set_attribute("faas.execution", context.request_id)

                    result = func(event, context)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper

    def capture_method(self, func):
        """
        Decorator for tracing class methods.
        Creates a span for the method execution.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine span name - use class name if available
            span_name = func.__name__
            if args and hasattr(args[0], "__class__"):
                class_name = args[0].__class__.__name__
                span_name = f"{class_name}.{func.__name__}"

            with self.tracer.start_as_current_span(span_name) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper

    @contextmanager
    def create_segment(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for creating trace segments (spans).

        Args:
            name: Name of the segment/span
            metadata: Optional dictionary of attributes to add to the span
        """
        with self.tracer.start_as_current_span(name) as span:
            try:
                # Add metadata as span attributes
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            span.set_attribute(key, value)
                        else:
                            # Convert complex types to string
                            span.set_attribute(key, str(value))

                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    @contextmanager
    def create_subsegment(self, name: str):
        """
        Context manager for creating subsegments (child spans).

        Args:
            name: Name of the subsegment/span
        """
        with self.tracer.start_as_current_span(name) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
