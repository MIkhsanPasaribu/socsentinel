# SOCsentinel — Complete Setup Guide

Panduan lengkap untuk setup SOCsentinel dari nol hingga running, baik untuk development lokal maupun production deployment.

---

## Daftar Isi

1. [Apa Itu SOCsentinel?](#apa-itu-socsentinel)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [Prerequisites (Yang Harus Diinstall Dulu)](#prerequisites)
4. [Step-by-Step: Setup Lokal (Mock Mode)](#step-by-step-setup-lokal-mock-mode)
5. [Penjelasan Lengkap Environment Variables](#penjelasan-lengkap-environment-variables)
6. [Setup vLLM + Qwen3 (GPU Mode)](#setup-vllm--qwen3-gpu-mode)
7. [Docker Deployment](#docker-deployment)
8. [Hugging Face Spaces Deployment](#hugging-face-spaces-deployment)
9. [Testing](#testing)
10. [Cara Pakai Aplikasi](#cara-pakai-aplikasi)
11. [Troubleshooting (Solusi Error Umum)](#troubleshooting)
12. [FAQ](#faq)

---

## Apa Itu SOCsentinel?

SOCsentinel adalah sistem multi-agent AI yang mensimulasikan hierarki SOC (Security Operations Center) analyst. Sistem ini menggunakan 9 agent AI yang bekerja secara berurutan untuk menganalisis alert keamanan:

```
Alert Masuk
  -> Orchestrator (routing)
    -> L1 Triage (klasifikasi)
      -> Evidence Collector (kumpulkan bukti)
        -> MITRE Mapper (mapping ke ATT&CK)
          -> Detection Engineer (buat Sigma rule)
            -> Report Writer (buat laporan)
              -> Response Planner (buat playbook)
                -> Validator (review & approve)
                  -> Dashboard (analyst review)
```

### Dua Mode Operasi

| Mode | Kapan Dipakai | Butuh GPU? | Kecepatan |
|------|--------------|------------|-----------|
| **Mock** | Development, testing UI, demo cepat | Tidak | Instan (~1 detik) |
| **vLLM** | Production, demo final, hackathon submission | Ya (AMD MI300X) | ~8-15 detik |

**Untuk development lokal, gunakan Mock mode.** Semua fitur berfungsi sama persis, hanya response LLM yang menggunakan data dummy.

---

## Arsitektur Sistem

```
socsentinel/
├── backend/          <- Python FastAPI (port 8000)
│   ├── app/          <- Source code utama
│   ├── .venv/        <- Virtual environment (dibuat saat setup)
│   ├── .env          <- Environment variables (dibuat dari .env.example)
│   └── data/         <- ChromaDB + MITRE ATT&CK cache
│
├── frontend/         <- React + Vite + TailwindCSS (port 5173)
│   ├── src/          <- Source code utama
│   └── .env.local    <- Environment variables (dibuat dari .env.example)
│
├── docs/             <- Dokumentasi (file ini)
├── Dockerfile        <- Untuk deployment Docker/HF Spaces
└── docker-compose.yml
```

**Saat development**, kamu menjalankan 2 server terpisah:
- Backend di `http://localhost:8000`
- Frontend di `http://localhost:5173`

Frontend berkomunikasi dengan backend via REST API.

---

## Prerequisites

### Yang Harus Diinstall Sebelum Mulai

#### 1. Python 3.11+

**Cek apakah sudah terinstall:**
```bash
python --version
# Harus menampilkan: Python 3.11.x atau lebih tinggi
```

**Jika belum:**
- **Windows**: Download dari https://www.python.org/downloads/ -> centang "Add Python to PATH" saat install
- **macOS**: `brew install python@3.11`
- **Linux**: `sudo apt install python3.11 python3.11-venv`

#### 2. Node.js 18+

**Cek apakah sudah terinstall:**
```bash
node --version
# Harus menampilkan: v18.x.x atau lebih tinggi

npm --version
# Harus menampilkan: 9.x.x atau lebih tinggi
```

**Jika belum:**
- **Semua OS**: Download dari https://nodejs.org/ (pilih LTS version)

#### 3. Git

**Cek apakah sudah terinstall:**
```bash
git --version
```

**Jika belum:**
- **Windows**: Download dari https://git-scm.com/
- **macOS**: `xcode-select --install`
- **Linux**: `sudo apt install git`

#### 4. Docker (Opsional — hanya untuk deployment)

Tidak diperlukan untuk development lokal. Hanya diperlukan jika ingin deploy via Docker atau HF Spaces.

---

## Step-by-Step: Setup Lokal (Mock Mode)

Ikuti langkah-langkah ini secara berurutan. Setiap langkah harus berhasil sebelum lanjut ke langkah berikutnya.

### Langkah 1: Clone Repository

Buka terminal/PowerShell, navigasi ke folder tempat kamu ingin menyimpan project:

```bash
git clone https://github.com/your-org/socsentinel.git
cd socsentinel
```

Setelah ini, kamu seharusnya berada di folder `socsentinel/`.

### Langkah 2: Setup Backend

#### 2a. Masuk ke folder backend

```bash
cd backend
```

#### 2b. Buat Virtual Environment

Virtual environment adalah folder terisolasi yang berisi semua library Python khusus untuk project ini, supaya tidak bentrok dengan project lain.

```bash
python -m venv .venv
```

> **Catatan**: Jika command `python` tidak ditemukan, coba `python3`.

Setelah command ini, akan muncul folder `.venv/` di dalam `backend/`.

#### 2c. Aktifkan Virtual Environment

**Ini WAJIB dilakukan setiap kali buka terminal baru untuk bekerja di backend.**

```bash
# Windows PowerShell:
.venv\Scripts\activate

# Windows CMD:
.venv\Scripts\activate.bat

# Linux / macOS:
source .venv/bin/activate
```

**Tanda berhasil**: Prompt terminal berubah, ada `(.venv)` di depan:
```
(.venv) PS C:\...\socsentinel\backend>
```

> **Jika error "running scripts is disabled"** di Windows PowerShell:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Lalu coba aktifkan lagi.

#### 2d. Install Dependencies

```bash
pip install -r requirements.txt
```

Proses ini akan mengunduh dan menginstall ~50 library Python. Membutuhkan waktu 3-10 menit tergantung koneksi internet.

**Tanda berhasil**: Tidak ada error merah di akhir output. Mungkin ada warning kuning — itu normal.

> **Catatan tentang WeasyPrint**: Kamu mungkin melihat warning tentang WeasyPrint. Ini normal di Windows — PDF export hanya berfungsi di Linux/Docker. DOCX export tetap berfungsi di semua platform.

#### 2e. Buat File .env

File `.env` berisi konfigurasi yang spesifik untuk environment kamu (port, API keys, dll). File ini TIDAK di-commit ke Git.

```bash
# Windows:
copy .env.example .env

# Linux/macOS:
cp .env.example .env
```

#### 2f. Edit File .env

Buka file `backend/.env` dengan text editor (VS Code, Notepad++, dll) dan pastikan isinya seperti ini:

```env
# ========================================
# SOCsentinel Backend — Environment Variables
# ========================================

# === Server ===
ENVIRONMENT=development
PORT=8000
FRONTEND_URL=http://localhost:5173
DEBUG=false

# === LLM Configuration ===
# PENTING: Gunakan "mock" untuk development lokal tanpa GPU
# Ganti ke "vllm" hanya jika sudah setup vLLM server
LLM_PROVIDER=mock

# Pengaturan di bawah ini HANYA dipakai jika LLM_PROVIDER=vllm
# Biarkan default jika masih pakai mock
VLLM_BASE_URL=http://localhost:8000/v1
QWEN3_7B_MODEL=Qwen/Qwen3-7B
QWEN3_14B_MODEL=Qwen/Qwen3-14B
QWEN3_4B_MODEL=Qwen/Qwen3-4B
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_REQUEST_TIMEOUT=120

# === Vector Database (ChromaDB) ===
# Jangan diubah kecuali tahu apa yang dilakukan
CHROMA_PERSIST_DIR=./data/chroma_db
CHROMA_COLLECTION_NAME=mitre_attack

# === Embedding ===
EMBEDDING_MODEL=BAAI/bge-m3

# === NVD CVE API (Opsional) ===
# Daftar di: https://nvd.nist.gov/developers/request-an-api-key
# Tanpa API key tetap bisa jalan, tapi rate-limited
NVD_API_KEY=
NVD_API_URL=https://services.nvd.nist.gov/rest/json/cves/2.0

# === Threat Intel TAXII/STIX (Opsional) ===
# Biarkan kosong jika tidak punya TAXII server
TAXII_SERVER_URL=
TAXII_API_ROOT=
TAXII_COLLECTION_ID=
TAXII_TOKEN=

# === Observability ===
LOG_LEVEL=INFO
```

**Yang PALING PENTING**: `LLM_PROVIDER=mock` — ini yang menentukan apakah pakai LLM sungguhan atau mock.

#### 2g. Ingest Data MITRE ATT&CK

Script ini mengunduh database MITRE ATT&CK (697 teknik serangan) dan menyimpannya ke ChromaDB untuk digunakan oleh agent MITRE Mapper.

```bash
python -m scripts.ingest_mitre
```

**Output yang diharapkan:**
```
============================================================
  SOCsentinel -- MITRE ATT&CK Enterprise Ingestion
============================================================

[1/3] Downloading MITRE ATT&CK Enterprise Matrix...
[2/3] Extracting techniques from STIX bundle...
  -> Found 697 active techniques
[3/3] Ingesting 697 techniques into ChromaDB...
  Ingested 697/697 techniques (100.0%)

[OK] Complete! 697 techniques ingested in ~60s
============================================================
```

> **Catatan**: Run pertama membutuhkan ~60 detik karena mengunduh data. Run berikutnya lebih cepat karena menggunakan cache.

#### 2h. Jalankan Backend Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Penjelasan flag:**
- `--host 0.0.0.0` — bisa diakses dari browser
- `--port 8000` — port server
- `--reload` — auto-restart saat file berubah (untuk development)

**Output yang diharapkan:**
```
INFO:     SOCsentinel starting  environment=development llm_provider=mock
INFO:     MITRE ATT&CK knowledge base ready  techniques_count=697
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 2i. Verifikasi Backend Berjalan

Buka browser dan akses:

- **Health check**: http://localhost:8000/health
  ```json
  {
    "status": "healthy",
    "service": "socsentinel-backend",
    "version": "0.1.0",
    "llm_provider": "mock"
  }
  ```

- **API Documentation**: http://localhost:8000/docs — Swagger UI interaktif

**Jangan tutup terminal ini.** Backend harus tetap berjalan.

---

### Langkah 3: Setup Frontend

#### 3a. Buka Terminal Baru

Buka terminal/PowerShell **baru** (jangan tutup terminal backend). Navigasi ke folder project:

```bash
cd C:\path\ke\socsentinel\frontend
# Atau di Linux/macOS:
cd /path/ke/socsentinel/frontend
```

#### 3b. Install Dependencies

```bash
npm install
```

Proses ini mengunduh semua library JavaScript/React. Membutuhkan waktu 1-3 menit.

**Tanda berhasil**: Output terakhir menunjukkan `added xxx packages`.

#### 3c. Buat File .env.local

```bash
# Windows:
copy .env.example .env.local

# Linux/macOS:
cp .env.example .env.local
```

#### 3d. Edit File .env.local

Buka `frontend/.env.local` dan pastikan isinya:

```env
VITE_APP_NAME=SOCsentinel
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

> **PENTING**: `VITE_API_URL` harus mengarah ke backend yang sedang berjalan. Jika backend di port lain, sesuaikan.

#### 3e. Jalankan Frontend Dev Server

```bash
npm run dev
```

**Output yang diharapkan:**
```
  VITE v8.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

#### 3f. Buka Aplikasi

Buka browser dan akses: **http://localhost:5173**

Kamu seharusnya melihat dashboard SOCsentinel dengan sidebar navigasi di kiri.

---

### Langkah 4: Test Aplikasi

Sekarang kedua server berjalan. Mari test pipeline end-to-end:

1. **Buka halaman Alerts** (klik "Alerts" di sidebar)
2. **Generate alert**: Klik tombol "brute force" di bagian atas
3. **Investigate**: Klik tombol "Investigate" pada alert yang muncul
4. **Lihat pipeline**: Buka halaman "Investigation" — kamu akan melihat 9 agent bekerja secara berurutan via SSE streaming
5. **Lihat report**: Buka halaman "Reports" — klik pada investigation yang sudah selesai untuk melihat detail
6. **Export report**: Klik tombol "DOCX" untuk download laporan dalam format Word

---

## Penjelasan Lengkap Environment Variables

### Backend (`backend/.env`)

#### Server Configuration

| Variable | Nilai | Penjelasan |
|----------|-------|------------|
| `ENVIRONMENT` | `development` | Mode aplikasi. Pilihan: `development`, `testing`, `production`. Mempengaruhi logging dan error handling. |
| `PORT` | `8000` | Port tempat backend berjalan. Ubah jika port 8000 sudah dipakai. |
| `FRONTEND_URL` | `http://localhost:5173` | URL frontend untuk CORS (Cross-Origin Resource Sharing). Backend hanya menerima request dari URL ini. Untuk production, set ke `*` atau URL production. |
| `DEBUG` | `false` | Jika `true`, menampilkan stack trace detail di response error. Jangan aktifkan di production. |

#### LLM Configuration (Paling Penting)

| Variable | Nilai | Penjelasan |
|----------|-------|------------|
| `LLM_PROVIDER` | `mock` atau `vllm` | **Ini yang menentukan segalanya.** `mock` = tanpa GPU, response instan. `vllm` = pakai GPU AMD MI300X, response dari Qwen3. |
| `VLLM_BASE_URL` | `http://localhost:8000/v1` | URL server vLLM. Hanya dipakai jika `LLM_PROVIDER=vllm`. Format harus diakhiri `/v1` (OpenAI-compatible API). |
| `QWEN3_7B_MODEL` | `Qwen/Qwen3-7B` | Nama model 7B. Dipakai oleh: Orchestrator, Evidence Collector, MITRE Mapper, Detection, Validator, Threat Generator. |
| `QWEN3_14B_MODEL` | `Qwen/Qwen3-14B` | Nama model 14B. Dipakai oleh: Report Writer, Response Planner. Model lebih besar = output lebih detail. |
| `QWEN3_4B_MODEL` | `Qwen/Qwen3-4B` | Nama model 4B. Dipakai oleh: L1 Triage. Model lebih kecil = lebih cepat untuk klasifikasi sederhana. |
| `LLM_TEMPERATURE` | `0.3` | Kreativitas LLM (0.0 = deterministik, 1.0 = kreatif). Untuk SOC tasks, 0.3 optimal — cukup konsisten tapi tidak kaku. |
| `LLM_MAX_TOKENS` | `4096` | Panjang maksimum output LLM per request. 4096 cukup untuk semua agent. |
| `LLM_REQUEST_TIMEOUT` | `120` | Timeout dalam detik. Jika LLM tidak merespons dalam 120 detik, request gagal. |

#### RAG (Retrieval-Augmented Generation)

| Variable | Nilai | Penjelasan |
|----------|-------|------------|
| `CHROMA_PERSIST_DIR` | `./data/chroma_db` | Folder penyimpanan ChromaDB. Data MITRE ATT&CK disimpan di sini. |
| `CHROMA_COLLECTION_NAME` | `mitre_attack` | Nama collection di ChromaDB. Jangan diubah kecuali tahu apa yang dilakukan. |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Model embedding untuk mengubah teks menjadi vektor. BGE-M3 adalah model multilingual yang bagus. |

#### Threat Intelligence (Opsional)

| Variable | Nilai | Penjelasan |
|----------|-------|------------|
| `NVD_API_KEY` | (kosong) | API key dari NIST NVD untuk lookup CVE. Daftar gratis di https://nvd.nist.gov/developers/request-an-api-key. Tanpa key tetap bisa jalan tapi rate-limited (5 request/30 detik). |
| `TAXII_SERVER_URL` | (kosong) | URL server TAXII 2.1 untuk threat intel feeds. Biarkan kosong jika tidak punya. |

### Frontend (`frontend/.env.local`)

| Variable | Nilai | Penjelasan |
|----------|-------|------------|
| `VITE_APP_NAME` | `SOCsentinel` | Nama aplikasi yang ditampilkan di UI. |
| `VITE_API_URL` | `http://localhost:8000/api/v1` | URL backend API. **HARUS sesuai dengan port backend.** Jika backend di port 9000, ubah ke `http://localhost:9000/api/v1`. |
| `VITE_WS_URL` | `ws://localhost:8000/ws` | URL WebSocket. Untuk fitur real-time di masa depan. |

---

## Setup vLLM + Qwen3 (GPU Mode)

> **Kapan butuh ini?** Hanya jika kamu punya akses ke GPU AMD MI300X (atau compatible) dan ingin menjalankan LLM sungguhan. Untuk development dan testing UI, **TIDAK perlu setup ini** — gunakan `LLM_PROVIDER=mock`.

### Apa Itu vLLM?

vLLM adalah server inference LLM yang sangat cepat. Dia menyediakan API yang kompatibel dengan OpenAI, sehingga SOCsentinel bisa berkomunikasi dengannya seperti berkomunikasi dengan OpenAI API.

```
SOCsentinel Backend  --(HTTP)-->  vLLM Server  --(GPU)-->  Qwen3-14B Model
     (port 8000)                  (port 8000)              (AMD MI300X)
```

### Prerequisites untuk GPU Mode

- AMD Instinct MI300X GPU (192GB HBM3)
- ROCm 6.x terinstall
- Docker dengan ROCm support

### Opsi 1: vLLM via Docker (Paling Mudah)

```bash
# 1. Pull image vLLM yang sudah support ROCm
docker pull rocm/vllm:latest

# 2. Jalankan vLLM dengan model Qwen3-14B
docker run -d \
  --name vllm-qwen3 \
  --device /dev/kfd \
  --device /dev/dri \
  --group-add video \
  --shm-size 16g \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  rocm/vllm:latest \
  --model Qwen/Qwen3-14B \
  --tensor-parallel-size 1 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.9 \
  --dtype auto \
  --trust-remote-code

# 3. Tunggu sampai model selesai loading (~2-5 menit pertama kali)
# Cek log:
docker logs -f vllm-qwen3

# 4. Verifikasi berjalan:
curl http://localhost:8000/v1/models
```

**Penjelasan flag Docker:**
- `--device /dev/kfd --device /dev/dri` — akses ke GPU AMD
- `--group-add video` — permission untuk GPU
- `--shm-size 16g` — shared memory (penting untuk model besar)
- `-p 8000:8000` — map port 8000 host ke 8000 container
- `-v ~/.cache/huggingface:...` — cache model supaya tidak download ulang
- `--model Qwen/Qwen3-14B` — semua agent pakai model yang sama

### Opsi 2: AMD Developer Cloud

Jika menggunakan instance AMD Developer Cloud:

```bash
# 1. SSH ke instance
ssh user@<instance-ip>

# 2. Install vLLM
pip install vllm

# 3. Jalankan server
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-14B \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 8192 \
  --trust-remote-code

# 4. Catat IP address instance
hostname -I
```

### Menghubungkan SOCsentinel ke vLLM

Setelah vLLM berjalan, edit `backend/.env`:

```env
# UBAH dari mock ke vllm
LLM_PROVIDER=vllm

# Arahkan ke server vLLM
# Jika vLLM di mesin yang sama:
VLLM_BASE_URL=http://localhost:8000/v1

# Jika vLLM di mesin lain (AMD Developer Cloud):
# VLLM_BASE_URL=http://123.456.789.10:8000/v1

# All agents use the same Qwen3-14B model
QWEN3_7B_MODEL=Qwen/Qwen3-14B
QWEN3_14B_MODEL=Qwen/Qwen3-14B
QWEN3_4B_MODEL=Qwen/Qwen3-14B
```

Lalu restart backend:
```bash
# Ctrl+C untuk stop backend yang sedang jalan
# Jalankan ulang:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Verifikasi Koneksi vLLM

```bash
# 1. Test vLLM langsung
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-7B",
    "messages": [{"role": "user", "content": "What is a brute force attack?"}],
    "max_tokens": 100
  }'

# 2. Cek health SOCsentinel — harus menunjukkan llm_provider: "vllm"
curl http://localhost:8000/health
```

---

## Docker Deployment

### Build dan Jalankan

```bash
# Dari root folder socsentinel/
docker compose up --build -d

# Lihat log
docker compose logs -f socsentinel

# Cek health
curl http://localhost:7860/health

# Stop
docker compose down
```

### Dengan vLLM (Production)

Edit `docker-compose.yml`, ubah environment:

```yaml
services:
  socsentinel:
    environment:
      - LLM_PROVIDER=vllm
      - VLLM_BASE_URL=http://<ip-server-vllm>:8000/v1
```

---

## Hugging Face Spaces Deployment

1. Buat Space baru di https://huggingface.co/spaces
2. Pilih **Docker** sebagai SDK
3. Push repository ke Space:
   ```bash
   git remote add hf https://huggingface.co/spaces/<username>/<space-name>
   git push hf main
   ```
4. Dockerfile otomatis menangani build frontend + backend
5. Default mode: `LLM_PROVIDER=mock` (tidak butuh GPU)

Untuk menggunakan vLLM di HF Spaces:
- Buka Space Settings > Repository secrets
- Tambahkan: `LLM_PROVIDER` = `vllm`
- Tambahkan: `VLLM_BASE_URL` = `http://<ip-vllm>:8000/v1`

---

## Testing

### Backend Tests

```bash
cd backend

# Aktifkan venv dulu!
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Jalankan semua test
python -m pytest tests/ -v

# Jalankan dengan coverage report
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Jalankan test file tertentu
python -m pytest tests/test_pipeline.py -v

# Jalankan satu test spesifik
python -m pytest tests/test_api.py::test_health_endpoint -v
```

**Output yang diharapkan:**
```
tests/test_alerts.py::TestAlertGenerator::test_generate_specific_scenario PASSED
tests/test_api.py::test_health_endpoint PASSED
...
============================= 63 passed in 18s =============================
```

### Frontend Tests

```bash
cd frontend

# Type checking (cek error TypeScript)
npx tsc --noEmit

# Build production (termasuk type check)
npm run build
```

### Kapan Pakai Mock vs vLLM?

| Aktivitas | Mock | vLLM |
|-----------|------|------|
| Development UI/frontend | Pakai mock | Tidak perlu |
| Development backend/API | Pakai mock | Tidak perlu |
| Jalankan `pytest` | Pakai mock | Tidak perlu |
| Test kualitas response LLM | Tidak bisa | **Harus pakai vLLM** |
| Rekam demo video | Bisa | **Lebih bagus pakai vLLM** |
| Submit hackathon | Tidak cukup | **Harus pakai vLLM** |

**Kesimpulan**: Untuk development sehari-hari, `LLM_PROVIDER=mock` sudah cukup. Ganti ke `vllm` hanya saat perlu test kualitas output LLM atau rekam demo final.

---

## Cara Pakai Aplikasi

### Dashboard

Halaman utama menampilkan:
- **Stats**: Total investigations, auto-triage rate, avg response time
- **GPU Performance**: Metrik AMD MI300X
- **MITRE ATT&CK Heatmap**: Visualisasi teknik serangan yang terdeteksi
- **Agent Status**: Status 9 agent AI
- **Recent Investigations**: Daftar investigasi terbaru

### Alerts

1. Klik tombol skenario (brute_force, phishing, ransomware, dll) untuk generate alert sintetis
2. Setiap alert menampilkan: severity, rule name, source/dest IP, timestamp
3. Klik "Investigate" untuk memulai pipeline investigasi

### Investigation

1. Pilih skenario dari dropdown
2. Klik "Stream Investigation"
3. Lihat 9 agent bekerja secara real-time via SSE streaming
4. Setelah selesai, panel "Human-in-the-Loop Decision" muncul
5. Pilih: Approve Response / Escalate to L3 / Reject

### Reports

1. Semua investigasi yang selesai muncul di sini
2. Klik pada report card untuk expand detail
3. Detail meliputi: Executive Summary, Triage, IOCs, MITRE ATT&CK, Sigma Rule, Response Playbook, Validator Audit
4. Klik **DOCX** untuk download laporan Word
5. Klik **PDF** untuk download laporan PDF (hanya di Linux/Docker)

### Threat Hunting

Halaman untuk generate skenario threat hunting berdasarkan teknik MITRE ATT&CK.

### Audit Trail

Log semua aktivitas agent dan keputusan analyst.

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'xxx'"

**Penyebab**: Virtual environment belum diaktifkan, atau dependencies belum diinstall.

**Solusi**:
```bash
cd backend

# 1. Aktifkan venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# 2. Pastikan prompt berubah: (.venv) PS C:\...

# 3. Install ulang dependencies
pip install -r requirements.txt
```

### Error: "WeasyPrint not available" (Warning)

**Penyebab**: WeasyPrint membutuhkan system library (cairo, pango) yang tidak tersedia di Windows.

**Solusi**: Ini bukan error, hanya warning. PDF export tidak tersedia di Windows, tapi DOCX export tetap berfungsi. Di Docker/Linux, PDF export berfungsi normal.

### Error: "Investigation data expired" saat export

**Penyebab**: Data investigasi disimpan di memory (RAM) dan hilang saat server restart.

**Solusi**: Jalankan investigasi baru, lalu langsung export tanpa restart server.

### Error: "ECONNREFUSED" atau "Network Error" di frontend

**Penyebab**: Backend tidak berjalan, atau URL API salah.

**Solusi**:
```bash
# 1. Pastikan backend berjalan
curl http://localhost:8000/health

# 2. Jika tidak berjalan, start ulang:
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Pastikan frontend .env.local benar:
# VITE_API_URL=http://localhost:8000/api/v1
```

### Error: ChromaDB / "Collection not found"

**Penyebab**: Data MITRE ATT&CK belum di-ingest, atau folder data corrupt.

**Solusi**:
```bash
cd backend
.venv\Scripts\activate

# Hapus data lama dan ingest ulang
# Windows:
rmdir /s /q data\chroma_db
# Linux/macOS:
rm -rf data/chroma_db

# Ingest ulang
python -m scripts.ingest_mitre
```

### Error: "running scripts is disabled" (Windows PowerShell)

**Penyebab**: Execution policy PowerShell terlalu ketat.

**Solusi**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: vLLM "Connection refused"

**Penyebab**: Server vLLM belum berjalan atau port salah.

**Solusi**:
```bash
# 1. Cek apakah vLLM berjalan
curl http://localhost:8000/v1/models

# 2. Jika pakai Docker, cek container
docker ps | grep vllm
docker logs vllm-qwen3

# 3. Jika belum jalan, start ulang
docker start vllm-qwen3

# 4. Jika masih error, cek:
#    - GPU terdeteksi? rocm-smi
#    - Port bentrok? netstat -tlnp | grep 8000
#    - Memory cukup? Model 14B butuh ~33GB GPU memory
```

### Frontend: Halaman kosong / blank putih

**Penyebab**: Build error atau JavaScript crash.

**Solusi**:
```bash
cd frontend

# 1. Cek error TypeScript
npx tsc --noEmit

# 2. Jika ada error, perbaiki file yang disebutkan

# 3. Restart dev server
# Ctrl+C untuk stop
npm run dev
```

---

## FAQ

### Q: Apakah harus punya GPU untuk development?
**A**: Tidak. Gunakan `LLM_PROVIDER=mock` untuk development tanpa GPU. Semua fitur berfungsi sama, hanya response LLM yang menggunakan data dummy.

### Q: Berapa lama setup dari nol?
**A**: ~15-20 menit untuk mock mode (termasuk download dependencies dan MITRE data).

### Q: Apakah bisa pakai GPU NVIDIA?
**A**: Project ini dioptimalkan untuk AMD MI300X dengan ROCm, tapi vLLM juga support NVIDIA CUDA. Ganti `rocm/vllm:latest` dengan `vllm/vllm-openai:latest` di Docker command.

### Q: Data investigasi hilang setelah restart server?
**A**: Ya, karena data disimpan di memory (in-memory store). Ini by design untuk hackathon. Untuk production, perlu ditambahkan database (PostgreSQL/Redis).

### Q: Port 8000 sudah dipakai, bagaimana?
**A**: Ubah port di `backend/.env` (`PORT=9000`) dan jalankan dengan `--port 9000`. Jangan lupa update `frontend/.env.local` juga (`VITE_API_URL=http://localhost:9000/api/v1`).

### Q: Bisa deploy di Vercel/Netlify?
**A**: Frontend bisa di-deploy di Vercel/Netlify (static build). Backend harus di-deploy terpisah di server yang support Python (Railway, Render, HF Spaces, dll).
