"""
SOCsentinel — FastAPI application entry point.

Multi-Agent LLM Assistant for SOC Analysts.
Coordinates 9 specialized AI agents (Orchestrator, L1 Triage,
Evidence Collector, MITRE Mapper, Detection Engineer, Report Writer,
Response Planner, Validator, Threat Generator) for automated
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
            "detection engineering, and incident response using 9 specialized AI agents "
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
    from app.features.pipeline.sse import router as sse_router
    from app.features.pipeline.decision import router as decision_router
    from app.features.pipeline.benchmark import router as benchmark_router
    from app.features.detection.router import router as detection_router
    from app.features.response_planner.router import router as response_planner_router
    from app.features.validator.router import router as validator_router
    from app.features.threat_generator.router import router as threat_generator_router
    from app.features.threat_intel.router import router as threat_intel_router
    from app.features.soar_integration.router import router as soar_router
    from app.features.report_export.router import router as report_export_router

    api_prefix = settings.api_v1_prefix

    app.include_router(orchestrator_router, prefix=api_prefix)
    app.include_router(triage_router, prefix=api_prefix)
    app.include_router(evidence_router, prefix=api_prefix)
    app.include_router(mitre_router, prefix=api_prefix)
    app.include_router(report_router, prefix=api_prefix)
    app.include_router(alerts_router, prefix=api_prefix)
    app.include_router(siem_router, prefix=api_prefix)
    app.include_router(pipeline_router, prefix=api_prefix)
    app.include_router(sse_router, prefix=api_prefix)
    app.include_router(decision_router, prefix=api_prefix)
    app.include_router(benchmark_router, prefix=api_prefix)
    app.include_router(detection_router, prefix=api_prefix)
    app.include_router(response_planner_router, prefix=api_prefix)
    app.include_router(validator_router, prefix=api_prefix)
    app.include_router(threat_generator_router, prefix=api_prefix)
    app.include_router(threat_intel_router, prefix=api_prefix)
    app.include_router(soar_router, prefix=api_prefix)
    app.include_router(report_export_router, prefix=api_prefix)

    # Serve React frontend static files in production (HF Spaces)
    import os
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    if os.path.isdir(static_dir):
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            """Serve React SPA — fallback to index.html for client-side routing."""
            file_path = os.path.join(static_dir, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(static_dir, "index.html"))

        logger.info("Static frontend serving enabled", static_dir=static_dir)

    return app


# Create the app instance for uvicorn
app = create_app()
