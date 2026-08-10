"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings


def create_application() -> FastAPI:
    """Create the API with safe, environment-configured middleware."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json" if settings.docs_enabled else None,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.trusted_hosts,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_strings,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_application()
