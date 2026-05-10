# Copilot Instructions — SOCsentinel

## Project Overview

**SOCsentinel** is an open-source multi-agent LLM system that simulates the SOC (Security Operations Center) analyst hierarchy (L1, L2, L3) to automate alert triage, evidence collection, MITRE ATT&CK mapping, and investigation report generation.

Built with **Qwen3 + LangChain/AutoGen + FastAPI + React + AMD MI300X (ROCm)** targeting SOC teams in critical infrastructure organizations.

**Domain:** Web (Frontend + Backend separate) + AI/ML Agentic System
**Type:** Multi-repo style (frontend/ + backend/)
**Status:** Development (Hackathon — AMD Developer Hackathon May 2026)
**License:** MIT

---

## Mandatory Rules (Read Before Writing Any Code)

### 1. Language & Convention

- **Code comments & docstrings**: English (this is an international open-source hackathon project)
- **Variable & function names**: English with descriptive naming (snake_case for Python, camelCase for JS/TS)
- **File names**: Follow framework conventions (snake_case for Python, kebab-case/PascalCase for React)
- **UI strings**: English (international audience)
- **Libraries & packages**: Original names, not translated

### 2. Code Quality

- Follow best practices & patterns for each tech stack
- Code must be: readable, clean, maintainable, scalable, reliable
- No duplicate code — always extract to shared/utils
- Every function/class must have docstring/JSDoc comments
- Error handling mandatory in every async operation
- Input validation mandatory at all entry points (client + server)

### 3. Folder Structure

- **MUST use feature-based structure** — see Project Structure section
- Layer-based structure forbidden (controllers/, services/, models/ at root)
- Each feature is a self-contained unit
- Cross-feature imports only through public API (`__init__.py` / `index.ts`)

### 4. Change Process

Before implementing any changes:

1. Analyze impact on the existing system
2. State which files will be affected
3. Implement incrementally
4. Ensure no other functionality is broken
5. Check for duplication and clean up if found

---

## Project Structure

```
socsentinel/
├── frontend/                    # React 18 + TailwindCSS (Analyst Dashboard)
├── backend/                     # FastAPI (REST API + Agent Orchestration)
├── data/                        # MITRE ATT&CK data, synthetic alerts, CVE cache
│   ├── mitre_attack/            # ATT&CK Enterprise Matrix JSON
│   ├── synthetic_alerts/        # Generated SIEM alert datasets
│   └── cve_cache/               # Cached NVD CVE data
├── docs/                        # Project documentation
│   ├── architecture.md
│   ├── api.md
│   └── setup.md
├── .github/
│   ├── copilot-instructions.md  # This file
│   └── workflows/
│       ├── ci-backend.yml
│       ├── ci-frontend.yml
│       └── cd-production.yml
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── LICENSE
└── README.md
```

### Backend Structure (FastAPI + LangChain)

```
backend/
├── app/
│   ├── features/
│   │   ├── orchestrator/            # SOC Manager Agent
│   │   │   ├── __init__.py
│   │   │   ├── router.py            # /api/orchestrator endpoints
│   │   │   ├── service.py           # Orchestration logic
│   │   │   ├── agent.py             # Orchestrator agent definition
│   │   │   ├── schemas.py           # Pydantic request/response
│   │   │   └── tests/
│   │   ├── triage/                  # L1 Triage Agent
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── agent.py             # L1 triage agent
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   ├── evidence/                # Evidence Collector Agent (L2)
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── agent.py
│   │   │   ├── tools/               # IP lookup, CVE query, SIEM log tools
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ip_lookup.py
│   │   │   │   ├── cve_lookup.py
│   │   │   │   ├── domain_lookup.py
│   │   │   │   └── siem_query.py
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   ├── mitre_mapper/            # MITRE ATT&CK Mapper Agent (L2/L3)
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── agent.py
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   ├── report_writer/           # Report Writer Agent (Senior)
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── agent.py
│   │   │   ├── templates/           # Report templates
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   ├── alerts/                  # Alert management & synthetic generator
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── generator.py         # Synthetic alert generator
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   ├── pipeline/                # End-to-end investigation pipeline
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py           # Pipeline orchestration
│   │   │   ├── graph.py             # LangGraph workflow
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   └── audit/                   # Audit trail
│   │       ├── __init__.py
│   │       ├── router.py
│   │       ├── service.py
│   │       ├── schemas.py
│   │       └── tests/
│   │
│   ├── shared/
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── client.py            # LLM client factory (vLLM/Qwen3)
│   │   │   ├── prompt_manager.py    # Centralized prompt management
│   │   │   └── guardrails.py        # Safety guardrails
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py      # ChromaDB client
│   │   │   ├── embedder.py          # BGE-M3 embedding service
│   │   │   └── retriever.py         # Hybrid retriever
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── cors.py
│   │   │   └── rate_limiter.py
│   │   ├── siem/                    # SIEM connector abstraction
│   │   │   ├── __init__.py
│   │   │   └── connector.py         # BaseSIEMConnector, WazuhConnector, SyntheticConnector
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── handlers.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── scoring.py           # Confidence scoring utilities
│   │       └── formatting.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Pydantic BaseSettings
│   │   ├── logger.py                # Structured logging
│   │   └── dependencies.py          # FastAPI DI
│   │
│   └── main.py                      # FastAPI app entry
│
├── prompts/                          # Versioned prompt templates
│   └── v1/
│       ├── orchestrator_system.txt
│       ├── triage_system.txt
│       ├── evidence_system.txt
│       ├── mitre_mapper_system.txt
│       └── report_writer_system.txt
│
├── tests/
│   ├── conftest.py
│   └── evaluation/                   # LLM evaluation tests
│       ├── test_triage_accuracy.py
│       └── test_pipeline_e2e.py
│
├── .env
├── .env.example
├── pyproject.toml
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### Frontend Structure (React 18 + Vite + TailwindCSS)

```
frontend/
├── public/
│   ├── images/
│   └── icons/
├── src/
│   ├── features/
│   │   ├── dashboard/               # Main analyst dashboard
│   │   │   ├── components/
│   │   │   │   ├── DashboardView.tsx
│   │   │   │   ├── StatsOverview.tsx
│   │   │   │   └── AgentStatusPanel.tsx
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   ├── alerts/                  # Alert queue & triage view
│   │   │   ├── components/
│   │   │   │   ├── AlertQueue.tsx
│   │   │   │   ├── AlertCard.tsx
│   │   │   │   └── AlertDetail.tsx
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   ├── investigation/           # Investigation workflow view
│   │   │   ├── components/
│   │   │   │   ├── InvestigationTimeline.tsx
│   │   │   │   ├── EvidencePanel.tsx
│   │   │   │   ├── MitreAttackMap.tsx
│   │   │   │   └── AgentActivity.tsx
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   ├── reports/                 # Investigation report viewer
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   └── audit/                   # Audit trail viewer
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── services/
│   │       ├── types/
│   │       └── index.ts
│   │
│   ├── shared/
│   │   ├── components/
│   │   │   ├── ui/                  # Base UI components
│   │   │   ├── layout/             # Navbar, Sidebar, Layout
│   │   │   └── common/             # Modal, Table, Pagination
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   ├── api.ts              # Axios/fetch client setup
│   │   │   └── utils.ts
│   │   ├── stores/
│   │   └── types/
│   │
│   ├── core/
│   │   ├── config/
│   │   ├── constants/
│   │   ├── router/
│   │   │   └── router.tsx
│   │   └── providers/
│   │
│   ├── App.tsx
│   └── main.tsx
│
├── .env.local
├── .env.example
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Tech Stack

### Backend (Python)
- **Framework**: FastAPI (latest)
- **Language**: Python 3.11+
- **LLM Orchestration**: LangChain + AutoGen + LangGraph
- **LLM Backbone**: Qwen3 (7B/14B) via vLLM (ROCm build)
- **GPU Compute**: AMD Instinct MI300X (AMD Developer Cloud)
- **GPU Runtime**: ROCm 6.x
- **Vector DB**: ChromaDB (embedded, for MITRE ATT&CK RAG)
- **Embedding Model**: BAAI/bge-m3
- **Knowledge Base**: MITRE ATT&CK v16 Enterprise Matrix
- **CVE Database**: NVD API v2 (NIST)
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio
- **API Docs**: Swagger/OpenAPI (auto-generated by FastAPI)

### Frontend (TypeScript)
- **Framework**: React 18 (Vite)
- **Language**: TypeScript 5.x
- **Styling**: TailwindCSS v3
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Charts**: Recharts or Chart.js
- **Testing**: Vitest + Testing Library

### Infrastructure
- **Containerization**: Docker + docker-compose
- **Model Hub**: Hugging Face Hub / HF Spaces
- **LLM Serving**: vLLM (AMD ROCm build)
- **CI/CD**: GitHub Actions

---

## Architecture — Multi-Agent System

### Agent Definitions

| Agent | SOC Role | Model | Responsibility |
|-------|----------|-------|----------------|
| Orchestrator | SOC Manager | Qwen3-7B | Route alerts, prioritize, coordinate agents |
| L1 Triage | L1 Analyst | Qwen3-4B | Validate alerts, severity scoring, false positive filter |
| Evidence Collector | L2 Analyst | Qwen3-7B | Query SIEM logs, IP/domain lookup, CVE enrichment |
| MITRE Mapper | L2/L3 Analyst | Qwen3-7B | Map behaviors to MITRE ATT&CK TTPs, reconstruct timeline |
| Report Writer | Senior Analyst | Qwen3-14B | Generate structured investigation report |

### Pipeline Workflow

```
Raw SIEM Alert → Orchestrator (parse + prioritize)
  → L1 Triage (classify: Investigate / Close / Escalate)
    → Evidence Collector (enrich with IOCs, CVE, threat intel)
      → MITRE Mapper (map to ATT&CK techniques, build timeline)
        → Report Writer (generate investigation report)
          → Dashboard (human-in-loop: approve / escalate / reject)
```

### RAG Pipeline (MITRE ATT&CK)

```
MITRE ATT&CK JSON → Chunk by technique → Embed with BGE-M3
  → Store in ChromaDB → Query at inference time
  → Retrieve relevant techniques → Ground LLM response
```

---

## Features & Workflow

### Feature List

| No | Feature | Priority | Folder (Backend) | Folder (Frontend) |
|----|---------|----------|-------------------|--------------------|
| 1 | Alert Ingestion & Queue | Critical | features/alerts/ | features/alerts/ |
| 2 | Orchestrator Agent | Critical | features/orchestrator/ | features/dashboard/ |
| 3 | L1 Triage Agent | Critical | features/triage/ | features/alerts/ |
| 4 | Evidence Collection Agent | Critical | features/evidence/ | features/investigation/ |
| 5 | MITRE ATT&CK Mapper Agent | Critical | features/mitre_mapper/ | features/investigation/ |
| 6 | Report Writer Agent | Critical | features/report_writer/ | features/reports/ |
| 7 | Investigation Pipeline (E2E) | Critical | features/pipeline/ | features/investigation/ |
| 8 | Analyst Dashboard | Critical | — | features/dashboard/ |
| 9 | Synthetic Alert Generator | High | features/alerts/ | — |
| 10 | Audit Trail | High | features/audit/ | features/audit/ |
| 11 | Confidence Scoring | High | shared/utils/ | shared/components/ |
| 12 | MITRE ATT&CK RAG | Critical | shared/rag/ | — |

---

## Code Conventions

### Python (Backend)

```python
# ✅ CORRECT — English, descriptive, snake_case
alert_data = await fetch_alert_from_siem(alert_id)

async def classify_alert(alert: AlertInput) -> TriageResult:
    """Classify alert severity and determine if investigation is needed."""
    if not alert:
        raise ValueError("Alert data cannot be empty")
    return await triage_agent.classify(alert)

# ❌ WRONG — No docstring, no type hints
async def classify(a):
    return await agent.run(a)
```

### TypeScript (Frontend)

```typescript
// ✅ CORRECT — English, descriptive, camelCase
const alertData = await fetchAlertById(alertId);

/** Fetch all alerts with pagination and filtering */
async function fetchAllAlerts(filter: AlertFilter): Promise<Alert[]> {
  if (!filter) throw new Error('Filter cannot be empty');
  return await alertService.getAll(filter);
}
```

### API Response Structure

```python
# Standard API response — all endpoints MUST use this
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Any | None = None
    error: ErrorDetail | None = None
    pagination: PaginationInfo | None = None
    meta: ResponseMeta | None = None

class ErrorDetail(BaseModel):
    code: str            # 'VALIDATION_ERROR', 'NOT_FOUND', etc.
    detail: Any | None

class ResponseMeta(BaseModel):
    request_id: str
    processing_time_ms: float
    api_version: str
```

---

## Design Language

**Theme:** "Dark Ops" — reflecting real SOC environments (dark, precise, high-alert)

| Name | Hex | Usage |
|------|-----|-------|
| Deep Navy | `#0A1628` | Background, header, sidebar |
| Steel Blue | `#1E3A5F` | Card background, secondary elements |
| Cyan Electric | `#00D4FF` | Accent, AI activity indicator, active agent |
| Alert Orange | `#FF6B35` | Warning badge, high severity, escalation |
| Ice Gray | `#F0F4F8` | Table rows, input fields, subtle backgrounds |
| Success Green | `#10B981` | Resolved alerts, healthy status |
| Critical Red | `#EF4444` | Critical severity, errors |

---

## Environment Variables

### Backend (.env)
```env
# Server
ENVIRONMENT=development
PORT=8000
FRONTEND_URL=http://localhost:5173

# LLM Configuration
LLM_PROVIDER=vllm
VLLM_BASE_URL=http://localhost:8080/v1
QWEN3_7B_MODEL=Qwen/Qwen3-7B
QWEN3_14B_MODEL=Qwen/Qwen3-14B
QWEN3_4B_MODEL=Qwen/Qwen3-4B

# Vector Database (ChromaDB)
CHROMA_PERSIST_DIR=./data/chroma_db
CHROMA_COLLECTION_NAME=mitre_attack

# Embedding
EMBEDDING_MODEL=BAAI/bge-m3

# NVD API
NVD_API_KEY=
NVD_API_URL=https://services.nvd.nist.gov/rest/json/cves/2.0

# Observability
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```env
VITE_APP_NAME=SOCsentinel
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Git Convention

### Branch Naming
```
feature/[feature-name]     → New feature
fix/[bug-name]             → Bug fix
refactor/[area]            → Refactoring
release/[version]          → Release branch
hotfix/[description]       → Emergency fix
```

### Commit Messages
```
feat: [new feature description]
fix: [bug fix description]
refactor: [refactoring description]
docs: [documentation changes]
test: [test changes]
ci: [CI/CD changes]
chore: [maintenance tasks]
style: [formatting, no logic change]
```

---

## Pre-Commit Checklist

- [ ] All async operations have error handling (try/except or try/catch)
- [ ] All inputs have validation (Pydantic for Python, Zod for TypeScript)
- [ ] No hardcoded secrets or credentials
- [ ] No duplicate code
- [ ] All functions/classes have docstrings
- [ ] Type hints on all Python functions
- [ ] TypeScript strict mode, no unintentional `any`
- [ ] Feature-based structure followed
- [ ] Cross-feature imports through `__init__.py` / `index.ts`

---

## PROHIBITIONS

```
❌ DO NOT do this:
├── Layer-based structure (controllers/, models/ at root)
├── Business logic inside UI components
├── Hardcode environment variables or secrets
├── `any` type without strong reason (TypeScript)
├── Console.log / print() in production code
├── API calls directly from React components (must go via hook/service)
├── No error handling on async/await
├── Import internal files of other features (must go via __init__.py / index.ts)
├── Magic numbers/strings without constants
├── God function (> 200 lines) or God class
├── Skip input validation
├── Deploy without testing
├── Send security data to third-party cloud services
└── Use closed-source LLM APIs (must be self-hosted Qwen3)
```

---

## AI/ML Conventions

### Prompt Engineering
- All system prompts stored in `prompts/` directory (versioned: v1/, v2/)
- Use template variables, not hardcoded strings
- Every prompt must include role context and output format specification

### RAG Pipeline
- Chunk size: 500-1000 tokens for MITRE ATT&CK techniques
- Overlap: 10-20% of chunk size
- Embedding model: BGE-M3 (consistent across all RAG)
- Always include source references (technique ID, tactic) in answers

### LLM Error Handling
- Always handle: timeout, rate limit, token limit exceeded, model unavailable
- Implement retry with exponential backoff
- Fallback to smaller model if primary is unavailable
- Log all LLM interactions for audit trail

### Agent Design
- Each agent must produce structured output (Pydantic models)
- Confidence score (0.0 - 1.0) required for every agent decision
- Chain-of-evidence reasoning required (not just final answer)
- All agent outputs must be JSON-serializable for audit trail

---

## Hackathon Context

**Event:** AMD Developer Hackathon (lablab.ai)
**Track:** Track 1 — AI Agents & Agentic Workflows
**Duration:** May 5-8, 2026 (active build), submission May 11
**Target Prizes:** Grand Prize + Track 1 + Hugging Face Special Prize

### Judging Criteria Focus
1. **Application of Technology** — Qwen3 across 5 agents, ROCm, RAG, vLLM
2. **Originality** — Only open-source SOC agent with level-aware (L1/L2/L3)
3. **Business Value** — $36K/yr commercial alternative vs free open-source
4. **Presentation** — 3-min demo with real attack scenario, live dashboard
