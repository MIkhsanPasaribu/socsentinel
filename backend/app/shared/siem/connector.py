"""
SOCsentinel — SIEM connector abstraction.

Provides a pluggable interface for receiving alerts from
different SIEM platforms. Currently supports:
- Synthetic (built-in generator for demos)
- Wazuh (open-source SIEM via API/webhook)

To add a new SIEM: implement the BaseSIEMConnector interface.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.shared.schemas import AlertInput, Severity
from app.core.logger import get_logger

logger = get_logger(__name__)


class BaseSIEMConnector(ABC):
    """Abstract base class for SIEM connectors.

    All SIEM integrations must implement this interface
    to normalize alerts into SOCsentinel's AlertInput format.
    """

    @abstractmethod
    def normalize_alert(self, raw_event: dict) -> AlertInput:
        """Convert a raw SIEM event into a normalized AlertInput.

        Args:
            raw_event: Raw event dict from the SIEM platform.

        Returns:
            Normalized AlertInput instance.
        """
        ...

    @abstractmethod
    def get_connector_name(self) -> str:
        """Return the connector name (e.g., 'wazuh', 'elastic')."""
        ...


class WazuhConnector(BaseSIEMConnector):
    """Wazuh SIEM connector.

    Normalizes Wazuh alert JSON into SOCsentinel AlertInput format.
    Wazuh alerts come from the Wazuh API (GET /alerts) or via
    webhook integrations (wazuh-integratord).

    Wazuh alert structure:
    {
        "id": "1234567890.12345",
        "rule": {"id": "5710", "level": 10, "description": "..."},
        "agent": {"id": "001", "name": "web-server-01", "ip": "10.0.1.50"},
        "data": {"srcip": "203.0.113.42", "dstip": "10.0.1.50", ...},
        "decoder": {"name": "sshd"},
        "location": "/var/log/auth.log",
        "timestamp": "2026-05-05T10:00:00.000+0000",
        "full_log": "..."
    }
    """

    def get_connector_name(self) -> str:
        return "wazuh"

    def normalize_alert(self, raw_event: dict) -> AlertInput:
        """Convert a Wazuh alert into normalized AlertInput.

        Args:
            raw_event: Raw Wazuh alert dict.

        Returns:
            Normalized AlertInput.
        """
        rule = raw_event.get("rule", {})
        agent = raw_event.get("agent", {})
        data = raw_event.get("data", {})

        # Map Wazuh rule level (0-15) to SOCsentinel severity
        severity = self._map_wazuh_level(rule.get("level", 0))

        # Extract IPs from data section
        source_ip = (
            data.get("srcip", "")
            or data.get("src_ip", "")
            or data.get("srcUser", {}).get("ip", "")
            or ""
        )
        destination_ip = (
            data.get("dstip", "")
            or data.get("dst_ip", "")
            or agent.get("ip", "")
            or ""
        )

        # Extract ports
        source_port = self._safe_int(data.get("srcport"))
        destination_port = self._safe_int(data.get("dstport"))

        # Extract protocol
        protocol = data.get("protocol", "").upper()

        # Extract username
        username = (
            data.get("srcuser", "")
            or data.get("dstuser", "")
            or data.get("user", "")
            or ""
        )

        alert = AlertInput(
            alert_id=f"WAZUH-{raw_event.get('id', 'UNKNOWN')}",
            source="wazuh",
            timestamp=raw_event.get("timestamp", ""),
            rule_name=rule.get("description", "Unknown Wazuh Rule"),
            severity=severity,
            description=(
                f"[Wazuh Rule {rule.get('id', '?')}] {rule.get('description', 'N/A')} "
                f"(Level {rule.get('level', '?')}) on agent {agent.get('name', 'unknown')}"
            ),
            source_ip=source_ip,
            destination_ip=destination_ip,
            source_port=source_port,
            destination_port=destination_port,
            protocol=protocol,
            username=username,
            hostname=agent.get("name", ""),
            raw_log=raw_event.get("full_log", ""),
            metadata={
                "wazuh_rule_id": str(rule.get("id", "")),
                "wazuh_rule_level": str(rule.get("level", "")),
                "wazuh_agent_id": str(agent.get("id", "")),
                "wazuh_agent_name": agent.get("name", ""),
                "wazuh_decoder": raw_event.get("decoder", {}).get("name", ""),
                "wazuh_location": raw_event.get("location", ""),
                "wazuh_groups": ",".join(rule.get("groups", [])),
                "connector": "wazuh",
            },
        )

        logger.info(
            "Wazuh alert normalized",
            alert_id=alert.alert_id,
            rule_id=rule.get("id"),
            level=rule.get("level"),
            severity=severity.value,
        )
        return alert

    def _map_wazuh_level(self, level: int) -> Severity:
        """Map Wazuh rule level (0-15) to SOCsentinel severity.

        Wazuh levels:
        - 0-3:   Low (Informational, system events)
        - 4-7:   Medium (Low/medium priority events)
        - 8-11:  High (High priority events, attacks)
        - 12-15: Critical (Severe events, active exploit)

        Args:
            level: Wazuh rule level (0-15).

        Returns:
            SOCsentinel Severity enum.
        """
        if level >= 12:
            return Severity.CRITICAL
        elif level >= 8:
            return Severity.HIGH
        elif level >= 4:
            return Severity.MEDIUM
        elif level >= 1:
            return Severity.LOW
        else:
            return Severity.INFO

    def _safe_int(self, value: Any) -> int | None:
        """Safely convert a value to int, returning None on failure."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


class SyntheticConnector(BaseSIEMConnector):
    """Synthetic connector — wraps the built-in alert generator.

    Used for demos, testing, and hackathon presentations.
    """

    def get_connector_name(self) -> str:
        return "synthetic"

    def normalize_alert(self, raw_event: dict) -> AlertInput:
        """Pass-through for synthetic alerts (already in AlertInput format)."""
        return AlertInput(**raw_event)


# === Connector Registry ===

_CONNECTORS: dict[str, type[BaseSIEMConnector]] = {
    "wazuh": WazuhConnector,
    "synthetic": SyntheticConnector,
}


def get_connector(name: str) -> BaseSIEMConnector:
    """Get a SIEM connector instance by name.

    Args:
        name: Connector name ('wazuh', 'synthetic').

    Returns:
        Connector instance.

    Raises:
        ValueError: If connector name is not registered.
    """
    connector_cls = _CONNECTORS.get(name)
    if not connector_cls:
        raise ValueError(
            f"Unknown SIEM connector: '{name}'. Available: {list(_CONNECTORS.keys())}"
        )
    return connector_cls()
