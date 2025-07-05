"""
Sentry Integration for FastAPI
Initializes Sentry error tracking for backend services.
"""
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

# Call this at startup

def init_sentry(dsn: str, traces_sample_rate: float = 1.0):
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=traces_sample_rate,
        environment="production"
    )

    # Usage: wrap your FastAPI app
    # app = FastAPI(...)
    # app.add_middleware(SentryAsgiMiddleware)
