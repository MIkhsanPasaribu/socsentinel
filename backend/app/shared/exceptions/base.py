"""
SOCsentinel — Custom exception classes.

Centralized exception hierarchy for consistent error handling
across all agents and API endpoints.
"""


class SOCsentinelError(Exception):
    """Base exception for all SOCsentinel errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AgentError(SOCsentinelError):
    """Error raised when an agent fails to process a request."""

    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        super().__init__(
            message=f"Agent '{agent_name}' failed: {message}",
            code="AGENT_ERROR",
        )


class LLMError(SOCsentinelError):
    """Error raised when LLM interaction fails."""

    def __init__(self, message: str):
        super().__init__(message=message, code="LLM_ERROR")


class LLMTimeoutError(LLMError):
    """Error raised when LLM request times out."""

    def __init__(self, timeout_seconds: int):
        super().__init__(
            message=f"LLM request timed out after {timeout_seconds}s"
        )


class LLMRateLimitError(LLMError):
    """Error raised when LLM rate limit is exceeded."""

    def __init__(self):
        super().__init__(message="LLM rate limit exceeded. Please retry later.")


class RAGError(SOCsentinelError):
    """Error raised when RAG pipeline fails."""

    def __init__(self, message: str):
        super().__init__(message=message, code="RAG_ERROR")


class ValidationError(SOCsentinelError):
    """Error raised for input validation failures."""

    def __init__(self, message: str, details: dict | None = None):
        self.details = details
        super().__init__(message=message, code="VALIDATION_ERROR")


class NotFoundError(SOCsentinelError):
    """Error raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code="NOT_FOUND",
        )


class PipelineError(SOCsentinelError):
    """Error raised when the investigation pipeline fails."""

    def __init__(self, step: str, message: str):
        self.step = step
        super().__init__(
            message=f"Pipeline failed at step '{step}': {message}",
            code="PIPELINE_ERROR",
        )
