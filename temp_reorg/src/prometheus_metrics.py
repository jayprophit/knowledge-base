"""
Prometheus Metrics Integration for FastAPI
Exposes /metrics endpoint for Prometheus scraping.
"""
from prometheus_fastapi_instrumentator import Instrumentator

def setup_metrics(app):
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, include_in_schema=False, should_gzip=True)
