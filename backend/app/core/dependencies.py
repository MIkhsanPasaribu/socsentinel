"""
SOCsentinel — FastAPI dependency injection.

Provides singleton instances of shared services
(LLM client, vector store, settings) via FastAPI's Depends().
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings


# Type alias for injecting settings
SettingsDep = Annotated[Settings, Depends(get_settings)]
