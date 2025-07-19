# app/observability.py
from fastapi import FastAPI, Response
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

# 1) Define el recurso del servicio
resource = Resource.create({"service.name": "reviews-service"})

# 2) Configura TracerProvider (OpenTelemetry)
trace.set_tracer_provider(TracerProvider(resource=resource))

# 3) Configura MeterProvider con Prometheus reader
prom_reader = PrometheusMetricReader()
metrics.set_meter_provider(
    MeterProvider(resource=resource, metric_readers=[prom_reader])
)

# 4) Definir métricas personalizadas de Prometheus
REQUEST_COUNT = Counter(
    'http_server_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'http_server_request_latency_seconds',
    'Latency of HTTP requests in seconds',
    ['method', 'endpoint']
)
ERROR_COUNT = Counter(
    'http_server_errors_total',
    'Total HTTP error responses',
    ['method', 'endpoint', 'http_status']
)


def init_observability(app: FastAPI, mongo_client):
    """
    Instrumenta FastAPI y PyMongo con:
      - Contador de peticiones
      - Latencia de respuestas
      - Contador de errores
    Y expone endpoint /metrics para Prometheus.
    """
    # Instrumentación automática de trazas y métricas OTEL
    FastAPIInstrumentor().instrument_app(
        app,
        tracer_provider=trace.get_tracer_provider(),
        meter_provider=metrics.get_meter_provider(),
    )
    PymongoInstrumentor().instrument(mongo_client=mongo_client)

    # Middleware para recolectar métricas de cada petición
    @app.middleware('http')
    async def metrics_middleware(request, call_next):
        method = request.method
        endpoint = request.url.path
        # Mide latencia
        with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
            response = await call_next(request)
        status = response.status_code
        # Incrementa contador general
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            http_status=status
        ).inc()
        # Incrementa contador de errores si status>=400
        if status >= 400:
            ERROR_COUNT.labels(
                method=method,
                endpoint=endpoint,
                http_status=status
            ).inc()
        return response

    # Endpoint para que Prometheus raspee métricas
    @app.get('/metrics')
    async def metrics_endpoint():
        data = generate_latest(prom_reader._collector)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
