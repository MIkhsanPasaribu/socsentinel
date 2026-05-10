"""
SOCsentinel — CORS middleware configuration.

Configures Cross-Origin Resource Sharing for the frontend dashboard.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI, frontend_url: str) -> None:
    """Configure CORS middleware for the FastAPI app.

    Args:
        app: FastAPI application instance.
        frontend_url: Allowed frontend origin URL. Use '*' to allow all origins.
    """
    if frontend_url == "*":
        allowed_origins = ["*"]
    else:
        allowed_origins = [
            frontend_url,
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative dev port
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=frontend_url != "*",
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-request-id"],
    )
