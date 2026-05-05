"""
SOCsentinel — Prompt template manager.

Loads versioned prompt templates from the prompts/ directory
and renders them with variable substitution.
"""

from pathlib import Path
from string import Template

from app.core.logger import get_logger

logger = get_logger(__name__)

# Resolve prompts directory relative to backend root
PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "prompts"


def load_prompt(name: str, version: str = "v1") -> str:
    """Load a prompt template file by name and version.

    Args:
        name: Prompt file name without extension (e.g., 'orchestrator_system').
        version: Prompt version directory (default: 'v1').

    Returns:
        Raw prompt template string.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    path = PROMPTS_DIR / version / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")

    logger.debug("Loading prompt template", name=name, version=version)
    return path.read_text(encoding="utf-8")


def render_prompt(name: str, version: str = "v1", **kwargs: str) -> str:
    """Load and render a prompt template with variable substitution.

    Uses Python's string.Template for safe substitution ($variable syntax).

    Args:
        name: Prompt file name without extension.
        version: Prompt version directory.
        **kwargs: Template variables to substitute.

    Returns:
        Rendered prompt string.
    """
    template_str = load_prompt(name, version)
    template = Template(template_str)
    return template.safe_substitute(**kwargs)
