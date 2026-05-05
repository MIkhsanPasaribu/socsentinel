# 🛡️ SOCsentinel

**Multi-Agent LLM Assistant for SOC Analysts**

> Automating Level 1-3 SOC analyst workflows with 5 specialized AI agents powered by Qwen3 on AMD MI300X (ROCm).

[![AMD Developer Hackathon](https://img.shields.io/badge/AMD-Developer%20Hackathon%202026-ED1C24?style=for-the-badge&logo=amd)](https://hackathon.amd.com)
[![Track 1](https://img.shields.io/badge/Track-AI%20Agents%20%26%20Agentic%20Workflows-00D4FF?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)]()

---

## 🎯 Problem

Security Operation Centers face an unsustainable workload:

- **11,000** security alerts per day per SOC team
- **45 minutes** average triage time per alert
- **78%** analyst burnout rate
- **68%** of alerts go uninvestigated

SOCsentinel addresses this by deploying a multi-agent LLM system that automates L1-L3 triage, evidence collection, MITRE ATT&CK mapping, and report generation — reducing triage time from **45 minutes to under 5 minutes**.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Dashboard                       │
│              (Dark Ops Theme · TailwindCSS)              │
├─────────────────────────────────────────────────────────┤
│                    FastAPI Backend                        │
│                   /api/v1/* endpoints                    │
├─────────────────────────────────────────────────────────┤
│               5-Agent Investigation Pipeline             │
│                                                         │
│  ┌───────────┐  ┌─────────┐  ┌──────────┐  ┌────────┐ │
│  │Orchestrator│→│L1 Triage │→│ Evidence  │→│ MITRE  │ │
│  │ (Qwen3-7B)│  │(Qwen3-4B)│  │(Qwen3-7B)│  │Mapper  │ │
│  └───────────┘  └─────────┘  └──────────┘  │(Qwen3-7B)│ │
│                                             └────┬─────┘ │
│                                                  ↓       │
│                                           ┌──────────┐  │
│                                           │  Report   │  │
│                                           │  Writer   │  │
│                                           │(Qwen3-14B)│  │
│                                           └──────────┘  │
├─────────────────────────────────────────────────────────┤
│  ChromaDB (MITRE ATT&CK RAG)  │  vLLM (AMD MI300X)    │
└─────────────────────────────────────────────────────────┘
```

## 🤖 Agent Specializations

| Agent | Model | Role |
|-------|-------|------|
| **Orchestrator** | Qwen3-7B | Alert routing, priority assignment, workflow coordination |
| **L1 Triage** | Qwen3-4B | False positive detection, severity scoring, classification |
| **Evidence Collector** | Qwen3-7B | IOC enrichment, threat intel, CVE correlation |
| **MITRE Mapper** | Qwen3-7B | ATT&CK technique mapping, kill chain analysis (RAG-grounded) |
| **Report Writer** | Qwen3-14B | Investigation reports, executive summaries, recommendations |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
cp .env.example .env  # Edit as needed (LLM_PROVIDER=mock for local dev)

# Optional: Ingest MITRE ATT&CK data
python -m app.shared.rag.ingest

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/alerts/generate` | Generate synthetic alert |
| `POST` | `/api/v1/pipeline/investigate` | Run full 5-agent investigation |
| `POST` | `/api/v1/pipeline/investigate-demo` | Demo with synthetic alert |
| `GET` | `/api/v1/pipeline/list` | List all investigations |
| `GET` | `/api/v1/pipeline/status/{id}` | Get investigation status |
| `POST` | `/api/v1/orchestrator/route` | Route alert (standalone) |
| `POST` | `/api/v1/triage/classify` | Classify alert (standalone) |
| `POST` | `/api/v1/evidence/collect` | Collect evidence (standalone) |
| `POST` | `/api/v1/mitre/map` | Map to ATT&CK (standalone) |
| `POST` | `/api/v1/report/generate` | Generate report (standalone) |
| `POST` | `/api/v1/siem/wazuh/webhook` | Wazuh SIEM webhook receiver |
| `POST` | `/api/v1/siem/ingest` | Generic SIEM alert ingestion |

Interactive API docs available at `http://localhost:8000/docs`.

## 🛡️ Security Features

- **Prompt Injection Detection** — Blocks common injection patterns
- **PII Redaction** — Auto-redacts SSN, credit cards, emails from LLM output
- **Input Length Limits** — Prevents token abuse
- **CORS Middleware** — Configured frontend origin

## 🧪 Testing

```
48 tests passed ✅
├── test_alerts.py       — 5 tests (synthetic generator)
├── test_api.py          — 6 tests (API integration)
├── test_guardrails.py   — 10 tests (security guardrails)
├── test_llm_client.py   — 8 tests (mock LLM)
├── test_pipeline.py     — 5 tests (E2E pipeline)
└── test_siem.py         — 14 tests (Wazuh connector)
```

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Qwen3 (4B/7B/14B) via vLLM on AMD MI300X |
| **Backend** | FastAPI, Pydantic v2, LangChain |
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS |
| **RAG** | ChromaDB + MITRE ATT&CK Enterprise Matrix |
| **SIEM** | Wazuh (webhook integration) + Synthetic generator |
| **Infra** | AMD ROCm, Docker, Hugging Face Spaces |

## 📁 Project Structure

```
socsentinel/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, logging, dependencies
│   │   ├── features/       # Feature-based modules
│   │   │   ├── alerts/     # Synthetic alert generator
│   │   │   ├── evidence/   # Evidence Collector agent
│   │   │   ├── mitre_mapper/ # MITRE Mapper agent
│   │   │   ├── orchestrator/ # Orchestrator agent
│   │   │   ├── pipeline/   # E2E investigation pipeline
│   │   │   ├── report_writer/ # Report Writer agent
│   │   │   └── triage/     # L1 Triage agent
│   │   └── shared/         # Shared utilities
│   │       ├── exceptions/ # Error handling
│   │       ├── llm/        # LLM client, prompts, guardrails
│   │       ├── middleware/  # CORS
│   │       ├── rag/        # ChromaDB, retriever, ingestion
│   │       └── schemas.py  # Pydantic models
│   ├── prompts/v1/         # Versioned prompt templates
│   └── tests/              # 34 tests
├── frontend/
│   └── src/
│       ├── core/           # Router, providers
│       ├── features/       # Feature-based views
│       │   ├── alerts/     # Alert queue view
│       │   ├── dashboard/  # SOC dashboard
│       │   └── investigation/ # Pipeline results
│       └── shared/         # Components, types, utils
└── docker-compose.dev.yml
```

## 🏆 Hackathon Target

- **Grand Prize** — End-to-end multi-agent SOC platform
- **Track 1: AI Agents** — 5 specialized coordinated agents
- **Hugging Face Special Prize** — HF Spaces deployment
- **Build in Public** — Open development process

## 📝 License

MIT

---

Built with ❤️ for the [AMD Developer Hackathon 2026](https://hackathon.amd.com)