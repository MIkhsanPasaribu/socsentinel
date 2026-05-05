"""
SOCsentinel — Application configuration.

Centralized configuration using Pydantic BaseSettings.
All environment variables are validated and typed at startup.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # === Server ===
    environment: str = Field(default="development", description="Runtime environment")
    port: int = Field(default=8000, description="Server port")
    frontend_url: str = Field(
        default="http://localhost:5173", description="Frontend URL for CORS"
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # === LLM Configuration ===
    llm_provider: str = Field(
        default="vllm", description="LLM provider: vllm | mock"
    )
    vllm_base_url: str = Field(
        default="http://localhost:8080/v1",
        description="vLLM OpenAI-compatible API base URL",
    )
    qwen3_7b_model: str = Field(
        default="Qwen/Qwen3-7B", description="Qwen3 7B model name"
    )
    qwen3_14b_model: str = Field(
        default="Qwen/Qwen3-14B", description="Qwen3 14B model name"
    )
    qwen3_4b_model: str = Field(
        default="Qwen/Qwen3-4B", description="Qwen3 4B model name"
    )
    llm_temperature: float = Field(
        default=0.3, description="Default LLM temperature for SOC tasks"
    )
    llm_max_tokens: int = Field(
        default=4096, description="Maximum tokens per LLM request"
    )
    llm_request_timeout: int = Field(
        default=120, description="LLM request timeout in seconds"
    )

    # === Vector Database (ChromaDB) ===
    chroma_persist_dir: str = Field(
        default="./data/chroma_db", description="ChromaDB persistence directory"
    )
    chroma_collection_name: str = Field(
        default="mitre_attack", description="ChromaDB collection name"
    )

    # === Embedding ===
    embedding_model: str = Field(
        default="BAAI/bge-m3", description="Sentence transformer embedding model"
    )

    # === NVD CVE API ===
    nvd_api_key: str = Field(default="", description="NIST NVD API key (optional)")
    nvd_api_url: str = Field(
        default="https://services.nvd.nist.gov/rest/json/cves/2.0",
        description="NVD API base URL",
    )

    # === Observability ===
    log_level: str = Field(default="INFO", description="Logging level")

    # === API ===
    api_v1_prefix: str = Field(default="/api/v1", description="API version prefix")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings singleton."""
    return Settings()
