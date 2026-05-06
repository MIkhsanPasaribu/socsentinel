"""
SOCsentinel — STIX 2.1 parsing utilities.
"""

from typing import Any

from stix2 import parse as stix_parse


class STIXClient:
    """Parse STIX 2.1 bundles into normalized dictionaries."""

    def parse_bundle(self, bundle_json: dict[str, Any]) -> dict[str, Any]:
        """Parse a STIX bundle and return a normalized summary.

        Args:
            bundle_json: Raw STIX bundle JSON.

        Returns:
            Normalized STIX bundle summary.
        """
        bundle = stix_parse(bundle_json, allow_custom=True)
        objects = getattr(bundle, "objects", [])
        indicators = [obj for obj in objects if getattr(obj, "type", "") == "indicator"]
        attack_patterns = [
            obj for obj in objects if getattr(obj, "type", "") == "attack-pattern"
        ]
        relationships = [
            obj for obj in objects if getattr(obj, "type", "") == "relationship"
        ]

        return {
            "indicator_count": len(indicators),
            "attack_pattern_count": len(attack_patterns),
            "relationship_count": len(relationships),
            "indicators": [self._normalize_stix_obj(obj) for obj in indicators],
            "attack_patterns": [self._normalize_stix_obj(obj) for obj in attack_patterns],
        }

    def _normalize_stix_obj(self, obj: Any) -> dict[str, Any]:
        """Normalize a STIX object into a plain dict."""
        data = obj.serialize() if hasattr(obj, "serialize") else {}
        return {
            "id": data.get("id"),
            "type": data.get("type"),
            "name": data.get("name"),
            "description": data.get("description"),
            "pattern": data.get("pattern"),
            "valid_from": data.get("valid_from"),
            "labels": data.get("labels", []),
            "confidence": data.get("confidence"),
        }
