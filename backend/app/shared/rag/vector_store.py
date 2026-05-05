"""
SOCsentinel — ChromaDB vector store client.

Manages the MITRE ATT&CK knowledge base as an embedded
vector store for RAG-grounded agent reasoning.
"""

from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create the ChromaDB persistent client singleton."""
    global _client
    if _client is None:
        settings = get_settings()
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        _client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info("ChromaDB client initialized", persist_dir=str(persist_dir))
    return _client


def get_collection(name: str | None = None) -> chromadb.Collection:
    """Get or create the MITRE ATT&CK collection.

    Args:
        name: Collection name override. Defaults to config value.

    Returns:
        ChromaDB Collection instance.
    """
    global _collection
    if _collection is None:
        settings = get_settings()
        collection_name = name or settings.chroma_collection_name
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "MITRE ATT&CK Enterprise techniques for SOC RAG"},
        )
        logger.info(
            "ChromaDB collection ready",
            name=collection_name,
            count=_collection.count(),
        )
    return _collection


def add_documents(
    documents: list[str],
    metadatas: list[dict[str, Any]],
    ids: list[str],
) -> None:
    """Add documents to the vector store.

    Args:
        documents: List of text documents to embed and store.
        metadatas: List of metadata dicts for each document.
        ids: List of unique IDs for each document.
    """
    collection = get_collection()
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    logger.info("Documents added to vector store", count=len(documents))


def query_documents(
    query_text: str,
    n_results: int = 5,
    where: dict | None = None,
) -> dict:
    """Query the vector store for relevant documents.

    Args:
        query_text: The search query text.
        n_results: Number of results to return.
        where: Optional metadata filter.

    Returns:
        Dict with 'documents', 'metadatas', 'distances', 'ids' keys.
    """
    collection = get_collection()
    kwargs: dict[str, Any] = {
        "query_texts": [query_text],
        "n_results": min(n_results, collection.count() or n_results),
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)
    logger.debug(
        "Vector store query completed",
        query_preview=query_text[:80],
        results_count=len(results.get("ids", [[]])[0]),
    )
    return results


def reset_collection() -> None:
    """Delete and recreate the collection. Use with caution."""
    global _collection
    settings = get_settings()
    client = get_chroma_client()
    try:
        client.delete_collection(settings.chroma_collection_name)
    except Exception:
        pass
    _collection = None
    logger.warning("Vector store collection reset")
