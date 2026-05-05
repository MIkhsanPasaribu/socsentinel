"""
SOCsentinel — FastAPI application entry point.

Multi-Agent LLM Assistant for SOC Analysts.
Coordinates 5 specialized AI agents (Orchestrator, L1 Triage,
Evidence Collector, MITRE Mapper, Report Writer) for automated
security alert investigation.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logger import setup_logging, get_logger
from app.shared.exceptions.handlers import register_exception_handlers
from app.shared.middleware.cors import setup_cors

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager — handles startup and shutdown."""
    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info(
        "SOCsentinel starting",
        environment=settings.environment,
        llm_provider=settings.llm_provider,
    )

    # Initialize MITRE ATT&CK RAG on startup (non-blocking check)
    try:
        from app.shared.rag.vector_store import get_collection
        collection = get_collection()
        logger.info(
            "MITRE ATT&CK knowledge base ready",
            techniques_count=collection.count(),
        )
    except Exception as e:
        logger.warning(
            "MITRE ATT&CK knowledge base not initialized. Run ingestion first.",
            error=str(e),
        )

    yield

    # Cleanup on shutdown
    logger.info("SOCsentinel shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="SOCsentinel",
        description=(
            "Multi-Agent LLM Assistant for SOC Analysts. "
            "Automates alert triage, evidence collection, MITRE ATT&CK mapping, "
            "and investigation report generation using 5 specialized AI agents "
            "powered by Qwen3 on AMD MI300X (ROCm)."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Middleware
    setup_cors(app, settings.frontend_url)

    # Exception handlers
    register_exception_handlers(app)

    # Health check endpoint
    @app.get("/health", tags=["System"])
    async def health_check() -> dict:
        """Health check endpoint for monitoring and load balancers."""
        return {
            "status": "healthy",
            "service": "socsentinel-backend",
            "version": "0.1.0",
            "llm_provider": settings.llm_provider,
        }

    # Register feature routers
    from app.features.orchestrator.router import router as orchestrator_router
    from app.features.triage.router import router as triage_router
    from app.features.evidence.router import router as evidence_router
    from app.features.mitre_mapper.router import router as mitre_router
    from app.features.report_writer.router import router as report_router
    from app.features.alerts.router import router as alerts_router
    from app.features.alerts.siem_router import router as siem_router
    from app.features.pipeline.router import router as pipeline_router

    api_prefix = settings.api_v1_prefix

    app.include_router(orchestrator_router, prefix=api_prefix)
    app.include_router(triage_router, prefix=api_prefix)
    app.include_router(evidence_router, prefix=api_prefix)
    app.include_router(mitre_router, prefix=api_prefix)
    app.include_router(report_router, prefix=api_prefix)
    app.include_router(alerts_router, prefix=api_prefix)
    app.include_router(siem_router, prefix=api_prefix)
    app.include_router(pipeline_router, prefix=api_prefix)

    return app


# Create the app instance for uvicorn
app = create_app()
