# SOCsentinel — API Reference

Base URL: `http://localhost:8000`
API Prefix: `/api/v1`
Interactive Docs: `http://localhost:8000/docs`

---

## System

### Health Check

```
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "socsentinel-backend",
  "version": "0.1.0",
  "llm_provider": "mock"
}
```

---

## Alerts

### Generate Synthetic Alert

```
POST /api/v1/alerts/generate?scenario={scenario}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scenario` | string | No | One of: `brute_force`, `lateral_movement`, `data_exfiltration`, `phishing`, `ransomware`. Random if omitted. |

**Response:**

```json
{
  "success": true,
  "message": "Alert generated",
  "data": {
    "alert_id": "ALERT-81C4449A",
    "source": "synthetic",
    "timestamp": "2026-05-05T10:00:00Z",
    "rule_name": "Multiple Failed Login Attempts",
    "severity": "high",
    "description": "15 failed SSH login attempts from 203.0.113.42...",
    "source_ip": "203.0.113.42",
    "destination_ip": "10.0.1.50",
    "source_port": 44521,
    "destination_port": 22,
    "protocol": "SSH",
    "username": "root",
    "hostname": "web-server-01",
    "raw_log": "...",
    "metadata": { "scenario": "brute_force" }
  }
}
```

### Generate Batch

```
POST /api/v1/alerts/generate-batch?count={count}
```

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `count` | int | No | 5 | Number of alerts to generate (1-50). |

---

## SIEM Integration

### Wazuh Webhook

Receives raw Wazuh alert JSON and normalizes it.

```
POST /api/v1/siem/wazuh/webhook?auto_investigate={bool}
```

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `auto_investigate` | bool | No | `false` | Auto-trigger 8-agent pipeline. |

**Request Body:** Raw Wazuh alert JSON.

**Response:**

```json
{
  "success": true,
  "message": "Wazuh alert received: WAZUH-1620000001.123456",
  "data": {
    "alert_id": "WAZUH-1620000001.123456",
    "severity": "high",
    "rule_name": "sshd: Attempt to login using a denied user.",
    "source_ip": "203.0.113.42",
    "hostname": "web-server-01",
    "connector": "wazuh",
    "auto_investigate": false,
    "investigation_status": "pending_manual"
  }
}
```

### Generic SIEM Ingestion

```
POST /api/v1/siem/ingest?connector_name={name}&auto_investigate={bool}
```

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `connector_name` | string | No | `synthetic` | SIEM connector (`wazuh`, `synthetic`). |
| `auto_investigate` | bool | No | `false` | Auto-trigger pipeline. |

---

## Pipeline

### Run Investigation

```
POST /api/v1/pipeline/investigate
```

**Query Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `include_threat_scenario` | bool | No | `false` | Generate optional threat scenario step. |
| `threat_technique_id` | string | No | — | Override technique ID for threat scenario. |

**Request Body:** `AlertInput` JSON (same schema as `/alerts/generate` response).

**Response:**

```json
{
  "success": true,
  "message": "Investigation completed",
  "data": {
    "investigation_id": "INV-BC1D342C",
    "status": "completed",
    "orchestrator_result": { "priority": "high", "assigned_agent": "l1_triage", ... },
    "triage_result": { "classification": "investigate", "severity": "high", ... },
    "evidence_result": { "iocs": [...], "enrichment_summary": "...", ... },
    "mitre_result": { "techniques": [...], "kill_chain_phase": "...", ... },
    "detection_result": { "sigma_rule": "...", "confidence": 0.89, ... },
    "report_result": { "title": "...", "executive_summary": "...", "recommendations": [...] },
    "response_result": { "playbook_name": "...", "steps": [...], "confidence": 0.87 },
    "validator_result": { "is_approved": true, "risk_score": 0.22, "critic_comments": "..." },
    "audit_trail": [
      { "step": "orchestrator", "agent": "Orchestrator", "processing_time_ms": 25.7, "confidence": 0.85, "status": "completed" },
      ...
    ],
    "total_processing_time_ms": 59.3
  },
  "meta": { "investigation_id": "INV-BC1D342C", "processing_time_ms": 59.3 }
}
```

### Demo Investigation

```
POST /api/v1/pipeline/investigate-demo?scenario={scenario}
```

Generates a synthetic alert and runs the full pipeline in one call.

### List Investigations

```
GET /api/v1/pipeline/list
```

### Get Investigation Status

```
GET /api/v1/pipeline/status/{investigation_id}
```

### Stream Investigation (SSE)

```
GET /api/v1/pipeline/stream-investigate?scenario={scenario}&include_threat_scenario={bool}&threat_technique_id={id}
```

---

## Standalone Agent Endpoints

Each agent can be invoked individually for debugging or benchmarking.

### Orchestrator

```
POST /api/v1/orchestrator/route
Body: AlertInput JSON
```

### L1 Triage

```
POST /api/v1/triage/classify
Body: AlertInput JSON
```

### Evidence Collector

```
POST /api/v1/evidence/collect
Body: AlertInput JSON
```

### MITRE Mapper

```
POST /api/v1/mitre/map
Body: AlertInput JSON
```

### Report Writer

```
POST /api/v1/report/generate
Body: AlertInput JSON
```

### Detection Agent

```
POST /api/v1/detection/generate
Body: { "alert_data": { ... }, "mitre_result": { ... }, "evidence_result": { ... } }
```

### Response Planner

```
POST /api/v1/response-planner/generate
Body: { "alert_data": { ... }, "triage_result": { ... }, "evidence_result": { ... }, "mitre_result": { ... }, "report_result": { ... } }
```

### Validator

```
POST /api/v1/validator/validate
Body: { "alert_data": { ... }, "playbook_result": { ... } }
```

### Threat Scenario Generator

```
POST /api/v1/threat-generator/generate
Body: { "technique_id": "T1110", "apt_group": "generic", "target_sector": "general", "include_threat_intel": false }
```

### Threat Intel (TAXII)

```
POST /api/v1/threat-intel/fetch
Body: { "server_url": "https://example.com/taxii", "collection_id": "...", "api_root": "0", "token": "..." }
```

### SOAR Export

```
POST /api/v1/soar/export
Body: { "platform": "generic", "investigation_id": "INV-...", "payload": { ... } }
```

```
POST /api/v1/soar/export/{investigation_id}?platform=generic
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "error": {
    "code": "PIPELINE_ERROR",
    "detail": "Agent 'Orchestrator' LLM call failed: ..."
  }
}
```

**Error Codes:**
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Invalid request body |
| `PIPELINE_ERROR` | 500 | Pipeline execution failure |
| `AGENT_ERROR` | 500 | Individual agent failure |
| `GUARDRAIL_VIOLATION` | 400 | Prompt injection or invalid input |
| `NOT_FOUND` | 404 | Investigation ID not found |
