"""
SOCsentinel — Backend test configuration.
"""

import pytest
import asyncio


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
