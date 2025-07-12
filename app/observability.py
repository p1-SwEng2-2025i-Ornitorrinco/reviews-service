# app/observability.py
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor


# 1) Inicializar providers
resource = Resource.create(
    {"service.name": "reviews-service"}
)
trace.set_tracer_provider(TracerProvider(resource=resource))
metrics.set_meter_provider(MeterProvider(resource=resource))

# 2) Instrumentar FastAPI y Motor
def init_observability(app, mongo_client):
    FastAPIInstrumentor().instrument_app(app)
    # Instrumenta las operaciones de PyMongo (y por ende de Motor)
    PymongoInstrumentor().instrument()

