"""
SOCsentinel — FastAPI exception handlers.

Maps custom exceptions to standardized API error responses.
"""

import uuid
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.logger import get_logger
from app.shared.exceptions.base import (
    SOCsentinelError,
    AgentError,
    LLMError,
    LLMTimeoutError,
    LLMRateLimitError,
    NotFoundError,
    ValidationError,
    PipelineError,
)

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app.

    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic/FastAPI request validation errors."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        logger.warning(
            "Request validation failed",
            request_id=request_id,
            errors=exc.errors(),
            path=str(request.url),
        )
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Request validation failed",
                "error": {
                    "code": "VALIDATION_ERROR",
                    "detail": exc.errors(),
                },
                "meta": {"request_id": request_id},
            },
        )

    @app.exception_handler(NotFoundError)
    async def handle_not_found(
        request: Request, exc: NotFoundError
    ) -> JSONResponse:
        """Handle resource not found errors."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": exc.message,
                "error": {"code": exc.code},
                "meta": {"request_id": request_id},
            },
        )

    @app.exception_handler(ValidationError)
    async def handle_custom_validation(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle custom validation errors."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": exc.message,
                "error": {"code": exc.code, "detail": exc.details},
                "meta": {"request_id": request_id},
            },
        )

    @app.exception_handler(LLMTimeoutError)
    async def handle_llm_timeout(
        request: Request, exc: LLMTimeoutError
    ) -> JSONResponse:
        """Handle LLM timeout errors."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        logger.error("LLM timeout", request_id=request_id, message=exc.message)
        return JSONResponse(
            status_code=504,
            content={
                "success": False,
                "message": exc.message,
                "error": {"code": exc.code},
                "meta": {"request_id": request_id},
            },
        )

    @app.exception_handler(LLMRateLimitError)
    async def handle_llm_rate_limit(
        request: Request, exc: LLMRateLimitError
    ) -> JSONResponse:
        """Handle LLM rate limit errors."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": exc.message,
                "error": {"code": exc.code},
                "meta": {"request_id": request_id},
            },
        )

    @app.exception_handler(AgentError)
    async def handle_agent_error(
        request: Request, exc: AgentError
    ) -> JSONResponse:
        """Handle agent processing errors."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        logger.error(
            "Agent error",
            request_id=request_id,
            agent=exc.agent_name,
            message=exc.message,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": exc.message,
                "error": {"code": exc.code},
                "meta": {"request_id": request_id},
            },
        )

    @app.exception_handler(PipelineError)
    async def handle_pipeline_error(
        request: Request, exc: PipelineError
    ) -> JSONResponse:
        """Handle investigation pipeline errors."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        logger.error(
            "Pipeline error",
            request_id=request_id,
            step=exc.step,
            message=exc.message,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": exc.message,
                "error": {"code": exc.code, "detail": {"step": exc.step}},
                "meta": {"request_id": request_id},
            },
        )

    @app.exception_handler(SOCsentinelError)
    async def handle_socsentinel_error(
        request: Request, exc: SOCsentinelError
    ) -> JSONResponse:
        """Catch-all for any SOCsentinel custom errors."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        logger.error(
            "Application error",
            request_id=request_id,
            code=exc.code,
            message=exc.message,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": exc.message,
                "error": {"code": exc.code},
                "meta": {"request_id": request_id},
            },
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all for unhandled exceptions — prevents stack trace leakage."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        logger.error(
            "Unhandled exception",
            request_id=request_id,
            exc_type=type(exc).__name__,
            message=str(exc),
            path=str(request.url),
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "An internal server error occurred",
                "error": {"code": "INTERNAL_ERROR"},
                "meta": {"request_id": request_id},
            },
        )
