"""
SOCsentinel — Threat intel service.
"""

import asyncio
from typing import Any

from app.core.config import get_settings
from app.core.logger import get_logger
from app.shared.exceptions.base import ValidationError
from app.shared.threat_intel.feed_manager import ThreatIntelFeedManager

logger = get_logger(__name__)


async def fetch_threat_intel(
    server_url: str | None,
    api_root: str,
    collection_id: str | None,
    token: str | None = None,
) -> dict[str, Any]:
    """Fetch and parse threat intel from a TAXII server.

    Args:
        server_url: TAXII server URL.
        api_root: API root or index.
        collection_id: Collection ID.
        token: Optional bearer token.

    Returns:
        Parsed threat intel summary.
    """
    settings = get_settings()
    resolved_server_url = server_url or settings.taxii_server_url
    resolved_collection_id = collection_id or settings.taxii_collection_id
    resolved_api_root = api_root or settings.taxii_api_root
    resolved_token = token or settings.taxii_token

    if not resolved_server_url or not resolved_collection_id:
        raise ValidationError(
            message="TAXII server URL and collection ID are required",
            details={
                "server_url": bool(resolved_server_url),
                "collection_id": bool(resolved_collection_id),
            },
        )

    manager = ThreatIntelFeedManager(
        server_url=resolved_server_url,
        api_root=resolved_api_root,
        collection_id=resolved_collection_id,
        token=resolved_token or None,
    )
    result = await asyncio.to_thread(manager.fetch_and_parse)
    logger.info(
        "Threat intel fetched",
        indicator_count=result.get("indicator_count"),
        attack_pattern_count=result.get("attack_pattern_count"),
    )
    return result
