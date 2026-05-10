# SOCsentinel — Architecture Document

## System Overview

SOCsentinel is a **multi-agent LLM platform** that automates SOC (Security Operations Center) analyst workflows. It ingests security alerts from SIEM platforms (Wazuh), processes them through an 8-agent investigation pipeline powered by Qwen3 models on AMD MI300X GPUs, and produces actionable investigation reports.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         SIEM Sources                              │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────────┐  │
│  │  Wazuh   │  │   Synthetic  │  │  Future: Elastic / Splunk  │  │
│  │ Webhook  │  │  Generator   │  │     (pluggable connectors) │  │
│  └────┬─────┘  └──────┬───────┘  └────────────┬───────────────┘  │
│       │               │                       │                  │
│       └───────────────┼───────────────────────┘                  │
│                       ▼                                          │
│              ┌─────────────────┐                                 │
│              │ SIEM Connector  │  BaseSIEMConnector (ABC)        │
│              │   Normalizer    │  → Wazuh / Synthetic impls      │
│              └────────┬────────┘                                 │
└───────────────────────┼──────────────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (:8000)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Investigation Pipeline Service                │  │
│  │                                                            │  │
│  │  ┌──────────┐    ┌──────────┐    ┌───────────────────┐    │  │
│  │  │Orchestr- │    │L1 Triage │    │Evidence Collector │    │  │
│  │  │  ator    │───▶│  Agent   │───▶│     Agent         │    │  │
│  │  │(Qwen3-7B)│    │(Qwen3-4B)│    │   (Qwen3-7B)      │    │  │
│  │  └──────────┘    └──────────┘    └─────────┬─────────┘    │  │
│  │                                            │              │  │
│  │                                            ▼              │  │
│  │                              ┌───────────────────┐        │  │
│  │                              │   MITRE Mapper    │        │  │
│  │                              │   (Qwen3-7B)      │        │  │
│  │                              │  + RAG Context     │        │  │
│  │                              └─────────┬─────────┘        │  │
│  │                                        │                  │  │
│  │                                        ▼                  │  │
│  │                         ┌──────────────────────┐          │  │
│  │                         │  Threat Generator    │          │  │
│  │                         │   (optional)         │          │  │
│  │                         └─────────┬────────────┘          │  │
│  │                                   ▼                       │  │
│  │                              ┌───────────────────┐        │  │
│  │                              │   Detection Agent │        │  │
│  │                              │    (Qwen3-7B)     │        │  │
│  │                              └─────────┬─────────┘        │  │
│  │                                        ▼                  │  │
│  │                              ┌───────────────────┐        │  │
│  │                              │  Report Writer    │        │  │
│  │                              │  (Qwen3-14B)      │        │  │
│  │                              └─────────┬─────────┘        │  │
│  │                                        ▼                  │  │
│  │                              ┌───────────────────┐        │  │
│  │                              │ Response Planner  │        │  │
│  │                              │  (Qwen3-14B)      │        │  │
│  │                              └─────────┬─────────┘        │  │
│  │                                        ▼                  │  │
│  │                              ┌───────────────────┐        │  │
│  │                              │    Validator      │        │  │
│  │                              │   (Qwen3-7B)      │        │  │
│  │                              └───────────────────┘        │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Guardrails   │  │ Prompt Mgr   │  │ Agent Runner (base)    │ │
│  │ (injection,  │  │ (versioned   │  │ (invoke, parse JSON,   │ │
│  │  PII redact) │  │  templates)  │  │  audit, timing)        │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │                    RAG Pipeline                               ││
│  │  ChromaDB ◄── MITRE ATT&CK Enterprise Matrix (800+ techs)   ││
│  │  Retriever → format_techniques_for_prompt() → LLM context    ││
│  └──────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                   LLM Infrastructure                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               vLLM on AMD MI300X (ROCm)                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                │  │
│  │  │ Qwen3-4B │  │ Qwen3-7B │  │Qwen3-14B │                │  │
│  │  │ (Triage) │  │ (5+ agents)│ │ (Report/IR)|               │  │
│  │  └──────────┘  └──────────┘  └──────────┘                │  │
│  └────────────────────────────────────────────────────────────┘  │
│  Mock mode available for local dev (no GPU required)             │
└──────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                  React Dashboard (:5173)                          │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │Dashboard │  │ Alert Queue  │  │  Investigation Viewer      │ │
│  │ (stats,  │  │ (generate,   │  │  (pipeline steps, agent    │ │
│  │  agents) │  │  investigate)│  │   output JSON, audit)      │ │
│  └──────────┘  └──────────────┘  └────────────────────────────┘ │
│                  TailwindCSS · "Dark Ops" Theme                  │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. SIEM Integration Layer

| Component            | Purpose                                                 |
| -------------------- | ------------------------------------------------------- |
| `BaseSIEMConnector`  | Abstract interface for SIEM normalization               |
| `WazuhConnector`     | Maps Wazuh alerts (levels 0-15) to SOCsentinel severity |
| `SyntheticConnector` | Pass-through for demo/testing alerts                    |
| `siem_router.py`     | Webhook endpoint for Wazuh integration                  |

**Wazuh Level → Severity Mapping:**

- Level 0: Info
- Level 1-3: Low
- Level 4-7: Medium
- Level 8-11: High
- Level 12-15: Critical

### 2. Agent Pipeline

Each agent follows the **unified agent runner** pattern:

```
System Prompt → LLM Invocation → JSON Extraction → Audit Entry
```

**Context chaining:** Each agent's output is passed as context to the next:

```
Orchestrator result → Triage context
Triage result → Evidence context
Evidence result → MITRE Mapper context (+ RAG)
MITRE mapping → Detection + (optional Threat Scenario)
Detection result → Report Writer context
Report → Response Planner → Validator
```

### 3. RAG Pipeline (MITRE ATT&CK)

1. **Ingestion** (`ingest.py`): Downloads MITRE ATT&CK Enterprise Matrix JSON, parses ~800 techniques, batch-inserts into ChromaDB
2. **Retrieval** (`retriever.py`): Queries ChromaDB with alert + evidence text, returns top-N relevant techniques
3. **Injection** (`prompt_manager.py`): Formats retrieved techniques and injects into MITRE Mapper's `$mitre_context` placeholder

### 4. Security Layer

| Feature                    | Implementation                                         |
| -------------------------- | ------------------------------------------------------ |
| Prompt Injection Detection | Regex patterns for common injection attempts           |
| PII Redaction              | Auto-redacts SSN, credit cards, emails from LLM output |
| Input Length Limits        | 15,000 character max to prevent token abuse            |
| CORS                       | Configured for frontend origin only                    |

### 5. Observability

- **Structured logging** via `structlog` (JSON format)
- **Audit trail** in PipelineState (agent name, confidence, timing, status)
- **Per-agent timing** (processing_time_ms injected into every response)

## Data Flow

```
1. Alert arrives (Wazuh webhook OR synthetic generator)
2. SIEM connector normalizes to AlertInput
3. Pipeline creates PipelineState with investigation_id
4. Orchestrator: routes + assigns priority
5. L1 Triage: classifies (investigate/close/escalate)
   └─ If "close" → pipeline completes early (false positive)
6. Evidence Collector: gathers IOCs, enriches threat context
7. MITRE Mapper: RAG retrieval → technique mapping + timeline
8. Optional Threat Generator: creates attack scenarios for hunting
9. Detection Agent: outputs Sigma rule for SIEM coverage
10. Report Writer: synthesizes all outputs → investigation report
11. Response Planner: drafts containment playbook
12. Validator: approves or rejects with risk scoring
13. PipelineState updated with all results + audit trail
```

## Deployment

- **Local dev**: Mock LLM (no GPU needed), `uvicorn --reload`
- **Production**: vLLM on AMD MI300X via ROCm, Docker containerized
- **Target**: Hugging Face Spaces (Gradio/Docker SDK)
