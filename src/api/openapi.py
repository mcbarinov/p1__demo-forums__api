from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def set_custom_openapi(app: FastAPI) -> None:
    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Demo Forums API",
            version="1.0.0",
            summary="Backend API for Demo Forums - A learning project for frontend technologies",
            routes=app.routes,
        )

        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "Bearer token authentication (preferred)",
            },
            "AuthTokenCookie": {
                "type": "apiKey",
                "in": "cookie",
                "name": "session_id",
                "description": "Authentication token stored in cookie",
            },
        }

        # Apply security globally (will be overridden for public endpoints)
        openapi_schema["security"] = [
            {"BearerAuth": []},
            {"AuthTokenCookie": []},
        ]

        # Remove security from public endpoints
        public_endpoints = {
            ("POST", "/api/auth/login"),
        }

        for path, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                if (method.upper(), path) in public_endpoints:
                    # Mark as public endpoint (no security required)
                    operation["security"] = []

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
