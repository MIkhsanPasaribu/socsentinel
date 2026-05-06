"""
SOCsentinel — Threat intelligence feed manager.
"""

from typing import Any

from app.core.logger import get_logger
from app.shared.threat_intel.stix_client import STIXClient
from app.shared.threat_intel.taxii_client import TAXIIClient

logger = get_logger(__name__)


class ThreatIntelFeedManager:
    """Coordinate TAXII retrieval and STIX parsing."""

    def __init__(
        self,
        server_url: str,
        api_root: str,
        collection_id: str,
        token: str | None = None,
    ):
        self._server_url = server_url
        self._taxii_client = TAXIIClient(server_url, api_root, collection_id, token)
        self._stix_client = STIXClient()

    def fetch_and_parse(self) -> dict[str, Any]:
        """Fetch TAXII collection objects and parse as STIX.

        Returns:
            Parsed STIX summary payload.
        """
        logger.info("Fetching TAXII collection", server_url=self._server_url)
        bundle = self._taxii_client.fetch_collection_objects()
        return self._stix_client.parse_bundle(bundle)
