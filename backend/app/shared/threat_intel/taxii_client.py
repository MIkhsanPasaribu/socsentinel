"""
SOCsentinel — TAXII 2.1 client wrapper.
"""

from typing import Any

from taxii2client.v21 import Server


class TAXIIClient:
    """Fetch STIX objects from TAXII 2.1 servers."""

    def __init__(
        self,
        server_url: str,
        api_root: str,
        collection_id: str,
        token: str | None = None,
    ):
        self._server_url = server_url
        self._api_root = api_root
        self._collection_id = collection_id
        self._token = token

    def fetch_collection_objects(self) -> dict[str, Any]:
        """Fetch STIX objects for the configured collection.

        Returns:
            STIX bundle as dict.
        """
        server = Server(self._server_url)
        api_root = server.api_roots[0]
        if self._api_root:
            try:
                api_root_index = int(self._api_root)
                api_root = server.api_roots[api_root_index]
            except ValueError:
                matches = [
                    root for root in server.api_roots
                    if getattr(root, "url", "") == self._api_root
                ]
                api_root = matches[0] if matches else server.api_roots[0]

        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        collection = api_root.collections.get(self._collection_id)
        return collection.get_objects(headers=headers)
