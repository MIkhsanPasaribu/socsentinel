# SOCsentinel
## Multi-Agent LLM Assistant for SOC Analysts

| Field | Detail |
|---|---|
| **Track** | Track 1: AI Agents & Agentic Workflows |
| **Tech Stack** | Qwen3, LangChain/AutoGen, AMD MI300X, ROCm, MITRE ATT&CK RAG |
| **Target Prize** | Grand Prize + Track 1 + Hugging Face Special Prize + Build in Public |
| **Duration** | May 5 - May 8, 2026 (4 days active build) |
| **Submission** | May 11, 2026 02:00 WIB |

---

## 1. Pernyataan Masalah

### 1.1 Konteks & Urgensi

Security Operation Centers (SOC) adalah garda terdepan pertahanan siber organisasi modern. Namun, skala ancaman yang terus meningkat menciptakan beban kerja yang tidak berkelanjutan bagi para analis manusia.

| Statistik Kritis | Fakta | Dampak |
|---|---|---|
| Alert Volume | ~4.484 alert/hari per analis (rata-rata) | Burnout dan alert fatigue masif |
| Alert Diabaikan | 67% alert tidak pernah diinvestigasi | Threat terlewat, breach tidak terdeteksi |
| Waktu Investigasi | 30-60 menit per kasus L2 manual | Response time lambat, MTTR tinggi |
| Breach Lifecycle | 241 hari rata-rata deteksi + containment | Kerugian finansial dan reputasi masif |
| False Positive Rate | >50% alert adalah false positive | Waktu analis terbuang untuk noise |

### 1.2 Gap yang Belum Terpecahkan

Existing SOC tools seperti SIEM, SOAR, dan XDR unggul dalam deteksi. Namun, investigasi dan respons masih sangat bergantung pada analis manusia. Solusi komersial yang ada (Dropzone AI, Elastic AI) bersifat closed-source, mahal ($36.000+/tahun), dan tidak dapat direproduksi secara akademis. Solusi open-source yang ada tidak menyediakan arsitektur multi-agent yang terspesialisasi per level analis (L1, L2, L3).

---

## 2. Solusi: SOCsentinel

SOCsentinel adalah sistem multi-agent LLM open-source yang mensimulasikan hierarki analis SOC (L1, L2, L3) secara otomatis. Setiap agen memiliki peran dan kemampuan yang terspesialisasi, terkoordinasi oleh agen Orchestrator, dan dijalankan di atas AMD Instinct MI300X GPU menggunakan ROCm.

### 2.1 Proposisi Nilai Utama

- **Open-source dan reproducible:** dirancang untuk evaluasi akademis dan publikasi ilmiah
- **Level-aware:** setiap agen merepresentasikan kemampuan analis di level tertentu (L1/L2/L3)
- **Explainable AI:** setiap keputusan disertai chain-of-evidence, bukan sekadar rekomendasi hitam-putih
- **AMD-native:** dioptimalkan untuk AMD MI300X menggunakan ROCm dan vLLM serving
- **MITRE ATT&CK grounded:** semua mapping dan reasoning berbasis framework standar industri

---

## 3. Arsitektur Sistem

### 3.1 Gambaran Umum Arsitektur

SOCsentinel menggunakan arsitektur multi-agent berbasis LangChain/AutoGen dengan lima agen terspesialisasi yang beroperasi dalam pipeline terkoordinasi. Semua inferensi LLM berjalan on-premise di AMD Developer Cloud, sehingga data keamanan tidak pernah keluar ke cloud pihak ketiga.

| Agen | Peran SOC | Kemampuan Utama | Model |
|---|---|---|---|
| Orchestrator Agent | SOC Manager | Routing alert, prioritisasi, koordinasi antar agen | Qwen3-7B |
| L1 Triage Agent | L1 Analyst | Validasi alert, severity scoring, false positive filter | Qwen3-4B |
| Evidence Collector Agent | L2 Analyst | Query SIEM log, IP/domain lookup, CVE enrichment | Qwen3-7B |
| MITRE Mapper Agent | L2/L3 Analyst | Map perilaku ke MITRE ATT&CK TTP, timeline rekonstruksi | Qwen3-7B |
| Report Writer Agent | Senior Analyst | Generate investigation report terstruktur, rekomendasi respons | Qwen3-14B |

### 3.2 Diagram Arsitektur

```
SIEM Alert / Log Input
         │
         ▼
  Orchestrator Agent
         │
    ┌────┴────────────────────────────────┐
    ▼                                     │
L1 Triage Agent                     CVE/NVD Database    Threat Intel Feeds
    │                │                    │
False Positive   Severity >= 6            │
    │                │                    │
    ▼                ▼                    ▼
Close & Log   Evidence Collector Agent ◄──── MITRE ATT&CK RAG
                     │
                     ▼
             MITRE Mapper Agent
                     │
                     ▼
             Report Writer Agent
                     │
                     ▼
         Human Analyst Dashboard
              │           │
           Escalate     Approve
              │           │
              ▼           ▼
     L3 Human Review   Automated Response / SOAR
```

---

## 4. Workflow & Use Case

### 4.1 Alur Kerja Utama (Happy Path)

| Langkah | Agen | Input | Output | Waktu Target |
|---|---|---|---|---|
| 1. Alert Ingestion | Orchestrator | Raw SIEM alert JSON | Alert parsed + prioritized queue | < 2 detik |
| 2. L1 Triage | L1 Triage Agent | Alert metadata, severity score | Classified: Investigate / Close / Escalate | < 10 detik |
| 3. Evidence Collection | Evidence Collector | IP, domain, hash, CVE IDs | Enriched threat context + IOC list | < 30 detik |
| 4. ATT&CK Mapping | MITRE Mapper | Behaviors, logs, TTPs | Mapped techniques + attack timeline | < 20 detik |
| 5. Report Generation | Report Writer | All agent outputs | Structured investigation report PDF | < 15 detik |
| 6. Human Decision | Analyst Dashboard | Report + confidence score | Approve response / Escalate / Reject | Human-in-loop |

### 4.2 Activity Diagram

```
● (Start)
│
▼ SIEM triggers alert
AlertIngested
│ Orchestrator routes
▼
L1Triage ──────────────────────────────────────────┐
│ (Severity >= 6)        (Critical Alert)           │ (False Positive Detected)
▼                              ▼                    │
EvidenceCollection      HighPriorityQueue           │
│ (Evidence Gathered)    │ (Skip to mapping)        │
└──────────┬─────────────┘                          │
           ▼                                        │
      MITREMapping                                  │
      │ (TTPs identified)                           │
      ▼                                             │
  ReportGeneration                                  │
  │ (Report ready)                                  │
  ▼                                                 │
HumanReview ◄───────────────────────────────────────┘
│ (Analyst approves)   │ (Complex threat)
▼                      ▼
AutoResponse       L3Escalation ──► Closed
      └──────────────────┘
                  ▼ (End)
```

### 4.3 Use Case Utama

| Use Case | Aktor | Deskripsi | Outcome |
|---|---|---|---|
| UC-01: Alert Triage Otomatis | L1 Agent | Sistem menerima alert SIEM, agent L1 mengevaluasi severity dan false positive secara otomatis | Alert diklasifikasi dalam < 10 detik tanpa intervensi manusia |
| UC-02: Evidence Enrichment | Evidence Agent | Agent mengambil konteks dari CVE database, threat intel feeds, dan log historis | IOC list terisi lengkap, konteks ancaman terbentuk |
| UC-03: ATT&CK Mapping | MITRE Agent | Perilaku yang terdeteksi dipetakan ke taktik dan teknik MITRE ATT&CK | Timeline serangan terrekonstruksi, posisi kill chain diketahui |
| UC-04: Report AutoGeneration | Report Agent | Semua output agen digabung menjadi laporan investigasi terstruktur | Analis mendapat laporan siap review dalam < 1 menit |
| UC-05: Human-in-Loop Decision | Analis + Dashboard | Analis meninjau laporan dan memutuskan: approve, eskalasi, atau reject | Keputusan terinformasi, auditability terjaga |
| UC-06: L1 to L2 Escalation | Orchestrator | Alert yang melewati threshold severity diarahkan otomatis ke agen L2 | Tidak ada alert kritis yang tertahan di queue L1 |

---

## 5. Fitur Sistem

### 5.1 Core Features

| Fitur | Deskripsi | Relevansi Hackathon |
|---|---|---|
| Multi-Agent Orchestration | Lima agen terspesialisasi beroperasi secara terkoordinasi dengan peran yang berbeda | Track 1: Agentic Workflow |
| Level-Aware Escalation | Sistem secara otomatis menentukan level investigasi yang diperlukan (L1/L2/L3) | Originality: pendekatan tiered belum ada di open-source |
| MITRE ATT&CK RAG | Knowledge base MITRE ATT&CK diembed sebagai vector store untuk grounding LLM | Application of Technology: advanced RAG beyond naive |
| Confidence Scoring | Setiap keputusan agent dilengkapi confidence score dan bukti pendukung | Business Value: reduces false trust in AI output |
| Human-in-Loop Dashboard | Analis manusia selalu memiliki kontrol final atas setiap keputusan respons | Business Value: enterprise-safe deployment |
| Synthetic Alert Generator | Generator dataset sintetis untuk simulasi berbagai skenario serangan | Demo: tidak perlu data real yang sensitif |
| Audit Trail | Semua langkah investigasi dicatat lengkap dengan reasoning dan evidence | Presentation: demonstrable transparency |
| AMD GPU Acceleration | Inferensi LLM dijalankan di AMD MI300X via ROCm dan vLLM | Core requirement: AMD Developer Cloud |

---

## 6. Technology Stack

### 6.1 Stack Lengkap

| Layer | Teknologi | Versi / Variant | Fungsi | Alasan Dipilih |
|---|---|---|---|---|
| LLM Backbone | Qwen3 (MoE) | Qwen3-7B / 14B | Core reasoning semua agen | Partner prize + dual thinking/non-thinking mode ideal SOC |
| Agent Framework | LangChain + AutoGen | Latest stable | Multi-agent orchestration | Disebutkan eksplisit di track requirements hackathon |
| GPU Compute | AMD Instinct MI300X | AMD Developer Cloud | LLM inference acceleration | Mandatory: hackathon compute resource |
| GPU Runtime | ROCm | ROCm 6.x | GPU software stack | AMD native, pengganti CUDA untuk AMD hardware |
| LLM Serving | vLLM | AMD ROCm build | High-throughput serving | Optimal throughput di MI300X, PagedAttention |
| Vector Store | ChromaDB | Latest | RAG untuk MITRE ATT&CK + CVE | Lightweight, embedded, cocok untuk PoC |
| Embedding Model | BGE-M3 | BAAI/bge-m3 | Document embedding | Multilingual, strong retrieval performance |
| Knowledge Base | MITRE ATT&CK v16 | Enterprise Matrix | Grounding TTP mapping | Standar industri global, open data |
| CVE Database | NVD API v2 | NIST | Vulnerability context | Official government database, real-time update |
| SIEM Simulator | Custom Python Generator | In-house | Synthetic alert generation | Demo tanpa data sensitif, reproducible evaluation |
| Frontend | React + TailwindCSS | React 18 | Analyst dashboard UI | Modern UI, cepat dibangun dalam waktu hackathon |
| Backend API | FastAPI (Python) | Latest | REST API layer | Async, cepat, cocok untuk integrasi agent |
| Model Hub | Hugging Face Hub | HF Spaces | Deployment dan sharing | Required untuk Hugging Face prize |
| Containerization | Docker + docker-compose | Latest | Reproducible environment | Easy setup untuk evaluasi dan replication |

### 6.2 Dependency Graph

```
AMD Developer Cloud
└── AMD Instinct MI300X GPU
    └── ROCm 6.x Runtime
        └── vLLM Serving
            │
            ├── Model Layer
            │   ├── Qwen3-7B / 14B
            │   └── BGE-M3 Embeddings
            │
            └── Knowledge Base
                ├── MITRE ATT&CK v16
                └── NVD CVE Database
                    └── ChromaDB VectorStore

Agent Layer
└── Orchestrator
    ├── L1 Triage ──────────────► ChromaDB VectorStore
    ├── Evidence Collector ──────► ChromaDB VectorStore
    ├── MITRE Mapper
    └── Report Writer
```

---

## 7. Color Palette & Design Language

SOCsentinel menggunakan design language bertema **"Dark Ops"** yang mencerminkan lingkungan SOC nyata, yaitu gelap, presisi, dan high-alert.

| Nama | Hex | Penggunaan |
|---|---|---|
| Deep Navy | `#0A1628` | Background utama, header section, sidebar |
| Steel Blue | `#1E3A5F` | Subheading, card background, secondary button |
| Cyan Electric | `#00D4FF` | Accent utama, AI activity indicator, highlight active agent |
| Alert Orange | `#FF6B35` | Warning badge, high severity alert, escalation button |
| Ice Gray | `#F0F4F8` | Table row alternate, card background, input field |

---

## 8. Timeline Pengerjaan

Hackathon berlangsung **4-11 Mei 2026**. Target tim: selesai tanggal 8 Mei, sehingga tanggal 8-10 digunakan untuk finalisasi, polish, dan recording demo video.

### 8.1 Timeline Harian

```
4 Mei  ████████░░░░░░░░░░░░  Riset Ide + Finalisasi Konsep
       ████████░░░░░░░░░░░░  Rancang Arsitektur Sistem

5 Mei  ░░░░████████░░░░░░░░  Setup AMD Developer Cloud + ROCm
       ░░░░████████░░░░░░░░  Deploy Qwen3 via vLLM on MI300X
       ░░░░████████░░░░░░░░  Build MITRE ATT&CK RAG Pipeline

6 Mei  ░░░░░░░░████████░░░░  Orchestrator + L1 Triage Agent
       ░░░░░░░░████████░░░░  Evidence Collector Agent
       ░░░░░░░░████████░░░░  MITRE Mapper + Report Writer Agent

7 Mei  ░░░░░░░░░░░░████████  FastAPI Backend + Agent Pipeline
       ░░░░░░░░░░░░████████  React Analyst Dashboard UI
       ░░░░░░░░░░░░████████  Synthetic Alert Generator + Testing

8 Mei  ░░░░░░░░░░░░░░██████  End-to-end Testing + Bug Fixing
       ░░░░░░░░░░░░░░██████  Deploy ke Hugging Face Space
       ░░░░░░░░░░░░░░██████  Recording Demo Video

9-10   ░░░░░░░░░░░░░░░░████  Slide Deck + README Finalisasi
Mei    ░░░░░░░░░░░░░░░░████  Social Media Build in Public Posts
       ░░░░░░░░░░░░░░░░████  Final Submission Review
```

### 8.2 Breakdown Tugas Harian

| Tanggal | Target Harian | Deliverable | Prioritas |
|---|---|---|---|
| 4 Mei (Senin) | Brainstorming ide, finalisasi arsitektur, bagi tugas tim | Dokumen desain ini + tech stack decision | 🔴 KRITIS |
| 5 Mei (Selasa) | Setup cloud, deploy Qwen3, bangun RAG MITRE ATT&CK, scaffold project | Working LLM endpoint + RAG pipeline | 🔴 KRITIS |
| 6 Mei (Rabu) | Bangun 5 agen (Orchestrator, L1, Evidence, MITRE, Report Writer) | Semua agent dapat berjalan secara individual | 🔴 KRITIS |
| 7 Mei (Kamis) | Integrasi pipeline agen, FastAPI backend, React dashboard | End-to-end demo pertama bisa berjalan | 🔴 KRITIS |
| 8 Mei (Jumat) | Testing, bug fixing, deploy HF Space, record video demo | Submission-ready project + video demo | 🔴 KRITIS |
| 9 Mei (Sabtu) | Polish slide deck, README, social media post #1 dan #2 | Slide final + GitHub README + 2 posts | 🟡 TINGGI |
| 10 Mei (Minggu) | Final review submission, buffer untuk fixing last-minute | Submitted project di lablab.ai | 🟡 TINGGI |

---

## 9. Pemetaan Kriteria Judging Hackathon

| Kriteria | Bobot | Strategi SOCsentinel | Bukti Konkret |
|---|---|---|---|
| Application of Technology | Tinggi | Qwen3 dipakai di 5 agen berbeda, ROCm untuk inferensi, RAG untuk grounding, vLLM untuk serving | Demo live di AMD MI300X, screenshot inference logs, benchmark latency |
| Originality | Tinggi | Satu-satunya open-source SOC agent yang level-aware (L1/L2/L3). Arsitektur multi-agent baru untuk cybersecurity | Comparison table vs existing tools, paper reference yang belum ada solusinya |
| Business Value | Tinggi | Target market: SOC team di critical infrastructure (energi, air, transport) | Cost comparison: $36K/tahun Dropzone vs gratis opensource. MTTR reduction demo |
| Presentation | Tinggi | 3 menit video demo dengan skenario serangan nyata, slide terstruktur, live dashboard | Rekomendasi: mulai rekam dari hari 8, edit rapi, narasi storytelling |

---

## 10. Submission Checklist

| Item | Status | Catatan |
|---|---|---|
| Public GitHub Repository (MIT License) | Target: 8 Mei | README lengkap, setup instructions, demo GIF |
| Demo Application URL | Target: 8 Mei | Deploy di HF Spaces atau Render.com |
| Hugging Face Space | Target: 8 Mei | Join HF organization AMD Developer Hackathon terlebih dahulu |
| Video Presentation (maks 3 menit) | Target: 8 Mei | Screen recording demo + narasi, upload ke YouTube |
| Slide Presentation | Target: 9 Mei | Maks 10 slide: problem, solution, arch, demo, impact |
| Cover Image (1280x720) | Target: 9 Mei | Dark theme, tampilkan nama project dan tagline |
| Social Media Post #1 (technical update) | Target: 6-7 Mei | Tag @lablab + @AIatAMD, screenshot agent berjalan |
| Social Media Post #2 (progress/feedback) | Target: 8 Mei | Tag @lablab + @AIatAMD, share demo link |
| AMD Developer feedback form | Target: 10 Mei | Feedback tentang ROCm dan AMD Developer Cloud |