"""
SOCsentinel — Unit tests for SIEM connectors.
"""

import pytest
from app.shared.siem.connector import WazuhConnector, SyntheticConnector, get_connector


# Sample Wazuh alert (realistic format from Wazuh docs)
SAMPLE_WAZUH_ALERT = {
    "id": "1620000001.123456",
    "rule": {
        "id": "5710",
        "level": 10,
        "description": "sshd: Attempt to login using a denied user.",
        "groups": ["syslog", "sshd", "authentication_failures"],
    },
    "agent": {
        "id": "001",
        "name": "web-server-01",
        "ip": "10.0.1.50",
    },
    "data": {
        "srcip": "203.0.113.42",
        "dstip": "10.0.1.50",
        "srcport": "44521",
        "dstport": "22",
        "protocol": "ssh",
        "srcuser": "root",
    },
    "decoder": {"name": "sshd"},
    "location": "/var/log/auth.log",
    "timestamp": "2026-05-05T10:00:00.000+0000",
    "full_log": "May  5 10:00:00 web-server-01 sshd[12345]: Failed password for root from 203.0.113.42 port 44521 ssh2",
}


class TestWazuhConnector:
    def setup_method(self):
        self.connector = WazuhConnector()

    def test_connector_name(self):
        assert self.connector.get_connector_name() == "wazuh"

    def test_normalize_basic(self):
        alert = self.connector.normalize_alert(SAMPLE_WAZUH_ALERT)
        assert alert.alert_id == "WAZUH-1620000001.123456"
        assert alert.source == "wazuh"
        assert alert.source_ip == "203.0.113.42"
        assert alert.destination_ip == "10.0.1.50"
        assert alert.source_port == 44521
        assert alert.destination_port == 22
        assert alert.protocol == "SSH"
        assert alert.username == "root"
        assert alert.hostname == "web-server-01"

    def test_severity_mapping_critical(self):
        event = {**SAMPLE_WAZUH_ALERT, "rule": {**SAMPLE_WAZUH_ALERT["rule"], "level": 14}}
        alert = self.connector.normalize_alert(event)
        assert alert.severity.value == "critical"

    def test_severity_mapping_high(self):
        alert = self.connector.normalize_alert(SAMPLE_WAZUH_ALERT)  # level 10
        assert alert.severity.value == "high"

    def test_severity_mapping_medium(self):
        event = {**SAMPLE_WAZUH_ALERT, "rule": {**SAMPLE_WAZUH_ALERT["rule"], "level": 5}}
        alert = self.connector.normalize_alert(event)
        assert alert.severity.value == "medium"

    def test_severity_mapping_low(self):
        event = {**SAMPLE_WAZUH_ALERT, "rule": {**SAMPLE_WAZUH_ALERT["rule"], "level": 2}}
        alert = self.connector.normalize_alert(event)
        assert alert.severity.value == "low"

    def test_severity_mapping_info(self):
        event = {**SAMPLE_WAZUH_ALERT, "rule": {**SAMPLE_WAZUH_ALERT["rule"], "level": 0}}
        alert = self.connector.normalize_alert(event)
        assert alert.severity.value == "info"

    def test_metadata_preserved(self):
        alert = self.connector.normalize_alert(SAMPLE_WAZUH_ALERT)
        assert alert.metadata["wazuh_rule_id"] == "5710"
        assert alert.metadata["wazuh_agent_id"] == "001"
        assert alert.metadata["wazuh_decoder"] == "sshd"
        assert alert.metadata["connector"] == "wazuh"

    def test_raw_log_preserved(self):
        alert = self.connector.normalize_alert(SAMPLE_WAZUH_ALERT)
        assert "sshd" in alert.raw_log
        assert "203.0.113.42" in alert.raw_log

    def test_missing_fields_handled(self):
        """Test with minimal Wazuh event (missing optional fields)."""
        minimal = {"id": "123", "rule": {"id": "1", "level": 3}, "agent": {}, "data": {}}
        alert = self.connector.normalize_alert(minimal)
        assert alert.alert_id == "WAZUH-123"
        assert alert.source_ip == ""
        assert alert.severity.value == "low"


class TestSyntheticConnector:
    def test_connector_name(self):
        connector = SyntheticConnector()
        assert connector.get_connector_name() == "synthetic"


class TestGetConnector:
    def test_get_wazuh(self):
        connector = get_connector("wazuh")
        assert isinstance(connector, WazuhConnector)

    def test_get_synthetic(self):
        connector = get_connector("synthetic")
        assert isinstance(connector, SyntheticConnector)

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown SIEM connector"):
            get_connector("splunk")
