"""
SOCsentinel — Backend test configuration.
"""

import asyncio
from pathlib import Path
import os
import sys

import pytest


# Ensure backend/ is on sys.path for app imports when running from repo root.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Ensure test env vars are set before any app imports.
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("CHROMA_PERSIST_DIR", "./data/test_chroma_db")
os.environ.setdefault("CHROMA_COLLECTION_NAME", "test_mitre_attack")
os.environ.pop("HF_HUB_ENABLE_HF_TRANSFER", None)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Force mock LLM provider for all tests."""
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "./data/test_chroma_db")
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_mitre_attack")
