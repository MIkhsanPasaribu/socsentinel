"""
SOCsentinel — Qwen3 Thinking Mode feature.

Provides an endpoint to toggle Chain-of-Thought (CoT) reasoning for agents.
When enabled, Qwen3 models will return their internal `<think>` blocks
in the audit trail.
"""

from typing import Any
from app.core.logger import get_logger

logger = get_logger(__name__)

# Global in-memory toggle for demo purposes
_THINKING_MODE_ENABLED = False

def get_thinking_mode() -> bool:
    """Check if Qwen3 thinking mode is enabled."""
    return _THINKING_MODE_ENABLED

def set_thinking_mode(enabled: bool) -> dict[str, Any]:
    """Toggle Qwen3 thinking mode."""
    global _THINKING_MODE_ENABLED
    _THINKING_MODE_ENABLED = enabled
    
    logger.info("Qwen3 thinking mode changed", enabled=enabled)
    
    return {
        "thinking_mode": enabled,
        "model_behavior": "chain_of_thought_enabled" if enabled else "direct_response",
        "description": "Agents will now include their internal reasoning process in the audit trail." if enabled else "Agents will provide direct answers without internal reasoning."
    }
