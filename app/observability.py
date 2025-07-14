# app/observability.py
from fastapi import FastAPI, Response
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
# Import correcto del exporter de Prometheus:
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

# 1) Define el recurso (nombre del servicio)
resource = Resource.create({"service.name": "reviews-service"})

# 2) Configura el provider de trazas
trace.set_tracer_provider(TracerProvider(resource=resource))

# 3) Configura el provider de métricas con un reader de Prometheus
prom_reader = PrometheusMetricReader()
metrics.set_meter_provider(
    MeterProvider(resource=resource, metric_readers=[prom_reader])
)

def init_observability(app: FastAPI, mongo_client):
    """
    Instrumenta FastAPI y PyMongo con OpenTelemetry
    y expone /metrics para Prometheus.
    """
    # Instrumentación automática de FastAPI endpoints
    FastAPIInstrumentor().instrument_app(app)
    # Instrumentación de operaciones de Mongo
    PymongoInstrumentor().instrument(mongo_client=mongo_client)

    # Endpoint para que Prometheus raspee métricas
    @app.get("/metrics")
    async def metrics_endpoint():
        # generate_latest toma el collector interno del reader
        data = generate_latest(prom_reader._metric_reader)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
