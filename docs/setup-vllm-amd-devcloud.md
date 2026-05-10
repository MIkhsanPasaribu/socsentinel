# 🎮 SOCsentinel — Full Deploy di AMD Developer Cloud (MI300X GPU)

Tutorial lengkap untuk deploy **seluruh SOCsentinel** (vLLM + Backend + Frontend) di satu AMD Developer Cloud GPU Droplet (MI300X 192GB). Semua berjalan di satu mesin -- simple, cepat, tanpa latency antar server.

---

## 📋 Ringkasan Arsitektur (All-in-One)

```text
┌─────────────────────────────────────────────────────────────┐
│              AMD Developer Cloud GPU Droplet                │
│              MI300X 192GB HBM3 + ROCm 6.x                  │
│                                                             │
│  ┌─────────────────┐    ┌──────────────────────────────┐    │
│  │  vLLM Server    │    │  SOCsentinel Backend          │    │
│  │  Qwen3-14B      │◄───│  FastAPI (port 8080)          │    │
│  │  (port 8000)    │    │  + Frontend (static files)    │    │
│  │  ~33GB VRAM     │    │  + ChromaDB (RAG)             │    │
│  └─────────────────┘    └──────────────────────────────┘    │
│                                                             │
│  GPU: ~33 GB / 192 GB    RAM: ~3 GB / 16+ GB               │
└─────────────────────────────────────────────────────────────┘
         ▲
         │ HTTP (port 8080)
         │
    Browser / User
```

**Kenapa all-in-one?**

- **Lebih murah** -- hanya bayar 1 server (GPU droplet sudah termasuk CPU + RAM)
- **Zero latency** -- vLLM dan backend di localhost, tidak ada network hop
- **Simple** -- 1 SSH, 1 setup, 1 destroy
- **Hackathon-optimized** -- minimal setup, maksimal impact

**Alur kerja:**

1. Buat GPU Droplet di AMD Developer Cloud
2. SSH ke droplet, install vLLM di ROCm
3. Start vLLM (Qwen3-14B) di background
4. Clone SOCsentinel, build frontend, setup backend
5. Start backend -- akses dari browser via IP droplet
6. Selesai -- full SOCsentinel dengan LLM sungguhan

**Resource usage:**

```text
vLLM Qwen3-14B:        ~33 GB VRAM (GPU) + ~2 GB RAM
SOCsentinel Backend:    ~200 MB RAM
ChromaDB:              ~100 MB RAM
Frontend (static):     0 MB (served by backend)
Node.js (build only):  ~500 MB RAM (temporary)
────────────────────
Total:  ~3 GB RAM  +  ~33 GB VRAM  (droplet punya 16+ GB RAM, 192 GB VRAM)
```

---

## 💰 Info Harga & Spesifikasi

| Item | Detail |
|------|--------|
| **GPU** | AMD Instinct MI300X |
| **VRAM** | 192 GB HBM3 |
| **Memory Bandwidth** | 5.3 TB/s |
| **Compute Units** | 304 CUs |
| **OS** | Ubuntu Linux + ROCm 6.x |
| **Region** | Atlanta (atl1) |
| **Harga** | ~$3.18/jam (cek AMD Dev Cloud untuk harga terbaru) |

> ⚠️ **PENTING**: GPU Droplet ditagih per jam selama aktif. **DESTROY droplet** setelah selesai demo untuk menghindari tagihan membengkak.

---

## 🚀 Step 1: Buat GPU Droplet

### 1.1 -- Buka AMD Developer Cloud

Buka link berikut di browser (login dulu jika belum):

```text
https://devcloud.amd.com/gpus/new?i=c558b6&region=atl1&size=gpu-mi300x1-192gb-devcloud&fleetUuid=4182e067-7467-4db3-b4db-2b63db59f531&appId=221160341&image=vllm-0-17-1&type=applications
```

Link ini sudah pre-configured dengan:

- **Region**: Atlanta (atl1)
- **Size**: `gpu-mi300x1-192gb-devcloud` (1x MI300X)
- **Image**: `vllm-0-17-1` (base image dengan ROCm)

### 1.2 -- Konfigurasi Droplet

Di halaman create droplet:

1. **Hostname**: Beri nama, misal `socsentinel-gpu`
2. **Authentication**: Pilih SSH Key (recommended) atau Password
   - Jika SSH Key: Upload public key kamu (`~/.ssh/id_rsa.pub`)
   - Jika Password: Buat password yang kuat
3. Klik **Create GPU Droplet**

### 1.3 -- Tunggu Provisioning

Droplet akan dibuat dalam 1-3 menit. Setelah selesai, catat **IP Address** droplet.

```text
Contoh IP: 143.198.xxx.xxx
```

---

## 🔑 Step 2: SSH & Verifikasi Environment

```bash
ssh root@YOUR_DROPLET_IP
```

### 2.1 -- Verifikasi GPU Terdeteksi

```bash
rocm-smi
```

**Output yang diharapkan:**

```text
========================= ROCm System Management Interface =========================
================================== Concise Info ====================================
Device  [Model]              Temp    Power    Partitions       SCLK   MCLK    Fan
                                     (Watts)  (Mem, Compute)
======  ===================  ======  =======  ===============  =====  ======  ====
0       AMD Instinct MI300X  39.0°C  145.0W   NPS1, SPX        ...    ...     0%
========================== End of ROCm SMI Log =====================================
```

Jika `rocm-smi` menampilkan GPU, lanjut. Jika tidak, lihat [Troubleshooting: GPU tidak terdeteksi](#rocm-gpu-tidak-terdeteksi).

### 2.2 -- Cek ROCm Version

```bash
cat /opt/rocm/.info/version
# atau
rocminfo | head -20
```

Catat versi ROCm (misal `6.3.x` atau `7.0.x`). Ini penting untuk install vLLM yang kompatibel.

### 2.3 -- Cek Python Version

```bash
python3 --version
```

vLLM butuh Python 3.10-3.13. Jika belum ada:

```bash
apt update && apt install -y python3 python3-pip python3-venv
```

---

## 📦 Step 3: Install vLLM di ROCm

> **Catatan**: Jika droplet image sudah include vLLM, cek dulu: `python3 -c "import vllm; print(vllm.__version__)"`. Jika sudah terinstall, skip ke [Step 4](#-step-4-start-vllm-qwen3-14b).

### Opsi A: Install via pip (Recommended)

Cara tercepat menggunakan `uv` (pip modern yang lebih cepat):

```bash
# Install uv
pip install uv

# Install vLLM untuk ROCm (auto-detect versi ROCm)
uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/ --system
```

Jika `uv` tidak tersedia atau bermasalah, gunakan `pip` langsung:

```bash
# Cek versi ROCm yang tersedia
curl -s https://wheels.vllm.ai/rocm/vllm | head -20

# Install vLLM dengan versi spesifik (contoh: ROCm 6.3)
pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/
```

Jika pip gagal resolve dependency, spesifikan versi eksak:

```bash
# Contoh untuk vLLM 0.18.0 + ROCm 7.0
pip install vllm==0.18.0+rocm700 \
  --extra-index-url https://wheels.vllm.ai/rocm/0.18.0/rocm700
```

### Opsi B: Install via Docker (Alternative)

Jika pip install bermasalah, gunakan official Docker image:

```bash
# Pull official vLLM ROCm image
docker pull vllm/vllm-openai-rocm:latest

# Jalankan vLLM server via Docker
docker run -d \
  --name vllm-qwen3 \
  --group-add=video \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  --device /dev/kfd \
  --device /dev/dri \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 \
  --ipc=host \
  vllm/vllm-openai-rocm:latest \
  --model Qwen/Qwen3-14B \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.85 \
  --dtype auto \
  --trust-remote-code

# Cek log
docker logs -f vllm-qwen3
```

> Jika pakai Docker, skip Step 4 (vLLM sudah running). Lanjut ke [Step 5](#-step-5-clone--setup-socsentinel).

### Opsi C: Build from Source (Jika Opsi A & B Gagal)

```bash
# Install build dependencies
apt update && apt install -y git build-essential cmake

# Clone vLLM
git clone https://github.com/vllm-project/vllm.git
cd vllm

# Set target GPU architecture (MI300X = gfx942)
export PYTORCH_ROCM_ARCH="gfx942"

# Install
pip install -e .
```

> Build from source bisa memakan waktu 30-60 menit.

### Verifikasi vLLM Terinstall

```bash
python3 -c "import vllm; print(vllm.__version__)"
```

Jika muncul versi (misal `0.18.0`) tanpa error, vLLM siap.

---

## 🤖 Step 4: Start vLLM (Qwen3-14B)

### Kenapa Single Model (Qwen3-14B)?

| Aspek | Detail |
|-------|--------|
| **VRAM** | ~33 GB dari 192 GB (17% saja) |
| **Sisa KV Cache** | ~130 GB -- bisa handle 50+ concurrent requests |
| **Kualitas** | 14B jauh lebih baik dari 7B untuk report writing, MITRE mapping, playbook |
| **Simplicity** | Semua agent pakai `Qwen/Qwen3-14B` -- satu nama, satu model, zero confusion |
| **vLLM limitation** | Tidak support multi-model per instance ([GitHub #13633](https://github.com/vllm-project/vllm/issues/13633)) |

### Start vLLM di Background (screen)

```bash
# Install screen
apt install -y screen

# Buat session
screen -S vllm

# Jalankan vLLM
python3 -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-14B \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.85 \
  --dtype auto \
  --trust-remote-code
```

> **Pertama kali**: Model Qwen3-14B (~28GB) akan diunduh dari Hugging Face. Membutuhkan 5-15 menit. Progress terlihat di terminal.

Tunggu sampai muncul:

```text
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Lalu **detach dari screen**: tekan `Ctrl+A`, lalu `D`.

vLLM sekarang berjalan di background.

### Verifikasi vLLM Running

```bash
curl http://localhost:8000/v1/models | python3 -m json.tool
```

**Output yang diharapkan:**

```json
{
  "data": [
    {"id": "Qwen/Qwen3-14B", "object": "model"}
  ]
}
```

### Test Chat Completion

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-14B",
    "messages": [
      {"role": "system", "content": "You are a SOC analyst."},
      {"role": "user", "content": "Classify this alert: Multiple failed SSH login attempts from IP 192.168.1.100"}
    ],
    "max_tokens": 200,
    "temperature": 0.3
  }'
```

Jika mendapat response JSON dengan analisis, vLLM siap.

---

## 📂 Step 5: Clone & Setup SOCsentinel

### 5.1 -- Install Dependencies Sistem

```bash
# Update packages
apt update

# Install Node.js 22 LTS (Vite 8 requires Node 20.19+ or 22.12+)
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs

# Install git (biasanya sudah ada)
apt install -y git

# Install system deps untuk WeasyPrint (PDF export)
apt install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Verifikasi
node --version   # harus v22+
npm --version
python3 --version
git --version
```

### 5.2 -- Clone Repository

```bash
cd /root
git clone https://github.com/MIkhsanPasaribu/socsentinel.git
cd socsentinel
```

### 5.3 -- Build Frontend

```bash
cd frontend

# Install dependencies
npm ci

# Build production bundle
npx vite build

# Hasil build ada di frontend/dist/
ls dist/
```

### 5.4 -- Copy Frontend Build ke Backend

Backend FastAPI sudah configured untuk serve static files dari folder `static/`:

```bash
# Copy frontend build ke backend static directory
cp -r dist/ ../backend/static/

# Verifikasi
ls ../backend/static/index.html
```

### 5.5 -- Setup Backend

```bash
cd /root/socsentinel/backend

# Buat virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 5.6 -- Ingest MITRE ATT&CK Data (RAG)

Agar *MITRE Mapper Agent* dapat bekerja, kita perlu men-download dan memasukkan ratusan teknik MITRE ATT&CK ke dalam ChromaDB di server ROCm.

```bash
cd /root/socsentinel/backend
source .venv/bin/activate

# Jalankan script ingest
python -m scripts.ingest_mitre
```
Tunggu hingga muncul pesan `[OK] Complete!` di terminal.

### 5.7 -- Konfigurasi Environment

```bash
# Copy template
cp .env.example .env

# Edit .env
nano .env
```

Ubah nilai berikut di `.env`:

```env
# === UBAH INI ===
ENVIRONMENT=production
PORT=8080
FRONTEND_URL=*
DEBUG=false

# === LLM: Pointing ke vLLM localhost ===
LLM_PROVIDER=vllm
VLLM_BASE_URL=http://localhost:8000/v1

# === All agents use the same Qwen3-14B model ===
QWEN3_7B_MODEL=Qwen/Qwen3-14B
QWEN3_14B_MODEL=Qwen/Qwen3-14B
QWEN3_4B_MODEL=Qwen/Qwen3-14B

# === LLM Settings ===
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_REQUEST_TIMEOUT=180
```

**Catatan penting:**

- `PORT=8080` -- backend di port 8080, karena port 8000 sudah dipakai vLLM
- `VLLM_BASE_URL=http://localhost:8000/v1` -- localhost karena vLLM di mesin yang sama
- `FRONTEND_URL=*` -- allow semua origin (untuk demo)
- `LLM_REQUEST_TIMEOUT=180` -- 3 menit timeout (model 14B butuh waktu lebih)

---

## ▶️ Step 6: Start SOCsentinel Backend

### 6.1 -- Jalankan di Background (screen)

```bash
# Buat screen session baru untuk backend
screen -S backend

cd /root/socsentinel/backend
source .venv/bin/activate

# Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Tunggu sampai muncul:

```text
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Static frontend serving enabled
```

Lalu **detach**: tekan `Ctrl+A`, lalu `D`.

### 6.2 -- Buka Firewall

```bash
# Buka port 8080 untuk akses dari browser
ufw allow 8080/tcp

# Opsional: buka port 8000 jika ingin akses vLLM langsung
ufw allow 8000/tcp
```

### 6.3 -- Verifikasi

```bash
# Health check backend
curl http://localhost:8080/health
```

**Output yang diharapkan:**

```json
{
  "status": "healthy",
  "service": "socsentinel-backend",
  "version": "0.1.0",
  "llm_provider": "vllm"
}
```

### 6.4 -- Akses dari Browser

Buka di browser:

```text
http://YOUR_DROPLET_IP:8080
```

Kamu seharusnya melihat **SOCsentinel dashboard** lengkap.

### 6.5 -- Test Full Pipeline

Di browser: buka **Investigations** tab, pilih scenario (misal "Brute Force"), klik **Stream Investigation**.

Atau via API:

```bash
curl -X POST http://localhost:8080/api/v1/pipeline/investigate-demo \
  -H "Content-Type: application/json" \
  -d '{"scenario": "brute_force"}'
```

Kamu seharusnya melihat 9 agent bekerja dengan response LLM nyata, waktu per agent sekitar 1.5-4 detik.

---

## ⚡ Step 7: Auto-Restart & Background Services

Untuk memastikan server tetap menyala (auto-restart) bahkan jika *instance* direboot, kita perlu membuat layanannya permanen.

### 7.1 -- vLLM Service

Cara membuatnya tergantung pada bagaimana Anda menginstall vLLM di Step 3:

**👉 JIKA ANDA MENGGUNAKAN OPSI A (Pip):**
Buat *systemd service*:
```bash
cat > /etc/systemd/system/vllm.service << 'EOF'
[Unit]
Description=vLLM Server (Qwen3-14B on MI300X)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=$(which python3) -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-14B \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.85 \
  --dtype auto \
  --trust-remote-code
Restart=on-failure
RestartSec=10
Environment="HF_HOME=/root/.cache/huggingface"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable vllm
systemctl start vllm
```

**👉 JIKA ANDA MENGGUNAKAN OPSI B (Docker):**
Anda **tidak butuh** `systemd`. Cukup beritahu Docker agar otomatis me-restart *container*-nya di latar belakang:
```bash
docker update --restart unless-stopped vllm-qwen3
```

### 7.2 -- SOCsentinel Backend Service

Karena backend FastAPI di-*setup* secara manual menggunakan *virtual environment*, kita butuh *systemd service*:

```bash
cat > /etc/systemd/system/socsentinel.service << 'EOF'
[Unit]
Description=SOCsentinel Backend (FastAPI)
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/socsentinel/backend
ExecStart=/root/socsentinel/backend/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=on-failure
RestartSec=5
Environment="PATH=/root/socsentinel/backend/.venv/bin:/usr/local/bin:/usr/bin"

[Install]
WantedBy=multi-user.target
EOF
```

### 7.3 -- Enable & Start Backend

```bash
systemctl daemon-reload
systemctl enable socsentinel
systemctl start socsentinel

# Cek status
systemctl status socsentinel
```

### 7.4 -- Perintah Berguna

```bash
# Lihat log real-time backend
journalctl -u socsentinel -f

# Lihat log real-time vLLM (jika instalasi via Docker)
docker logs -f vllm-qwen3

# Restart backend
systemctl restart socsentinel
```

---

## 🔍 Step 8: Monitoring & Performance

### GPU Monitoring

```bash
# Real-time GPU stats (refresh setiap 1 detik)
watch -n 1 rocm-smi

# Detail memory usage
rocm-smi --showmeminfo vram

# Temperature dan power
rocm-smi --showtemp --showpower
```

### vLLM Metrics

```bash
# vLLM built-in metrics endpoint
curl http://localhost:8000/metrics
```

### Expected Performance (SOCsentinel dengan Qwen3-14B)

| Metric | Nilai |
|--------|-------|
| **Per-Agent Latency** | 1.5s - 4s |
| **Full Pipeline (9 agents)** | 15-30s |
| **GPU Memory Used** | ~33 GB / 192 GB |
| **KV Cache Available** | ~130 GB |
| **Tokens/sec** | ~30-50 |
| **Max Concurrent Requests** | 50+ (berkat KV cache besar) |

---

## 🧹 Step 9: Cleanup (PENTING!)

### Setelah Selesai Demo -- Destroy Droplet

GPU Droplet ditagih per jam. **WAJIB destroy setelah selesai** untuk menghindari tagihan.

```text
1. Buka https://devcloud.amd.com/gpus
2. Temukan droplet "socsentinel-gpu"
3. Klik ... (more) -> Destroy
4. Konfirmasi destroy
```

### Sebelum Destroy -- Backup (Opsional)

```bash
# Backup model cache (supaya tidak download ulang ~28GB)
tar czf /tmp/hf-cache.tar.gz ~/.cache/huggingface
scp root@YOUR_DROPLET_IP:/tmp/hf-cache.tar.gz ./
```

---

## 🛠️ Troubleshooting

### vLLM: "No module named vllm"

vLLM belum terinstall. Ikuti [Step 3](#-step-3-install-vllm-di-rocm).

```bash
# Quick check
python3 -c "import vllm; print(vllm.__version__)"

# Jika error, install ulang
pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/
```

### vLLM: "HIP out of memory"

```bash
# Kurangi memory utilization
--gpu-memory-utilization 0.7

# Atau kurangi context length
--max-model-len 4096
```

### vLLM: Model download lambat

```bash
# Set Hugging Face mirror (opsional)
export HF_ENDPOINT=https://hf-mirror.com

# Atau download manual dulu
pip install huggingface-hub
huggingface-cli download Qwen/Qwen3-14B --local-dir ./models/Qwen3-14B

# Lalu serve dari local path
python3 -m vllm.entrypoints.openai.api_server \
  --model ./models/Qwen3-14B \
  --host 0.0.0.0 --port 8000 \
  --max-model-len 8192 --dtype auto --trust-remote-code
```

### vLLM: pip install gagal (dependency conflict)

```bash
# Gunakan virtual environment terpisah
python3 -m venv ~/vllm-env
source ~/vllm-env/bin/activate
pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/

# Jalankan vLLM dari env ini
~/vllm-env/bin/python -m vllm.entrypoints.openai.api_server ...
```

Atau gunakan Docker (lihat [Step 3 Opsi B](#opsi-b-install-via-docker-alternative)).

### Backend: "Connection refused" ke vLLM

```bash
# 1. Pastikan vLLM berjalan
curl http://localhost:8000/v1/models

# 2. Jika tidak:
screen -r vllm   # cek apakah masih running
# atau
systemctl status vllm

# 3. Pastikan .env benar
grep VLLM_BASE_URL /root/socsentinel/backend/.env
# Harus: VLLM_BASE_URL=http://localhost:8000/v1
```

### Backend: "LLM request timed out"

```bash
# Naikkan timeout di .env
nano /root/socsentinel/backend/.env
# Ubah: LLM_REQUEST_TIMEOUT=300

# Restart backend
systemctl restart socsentinel
```

### Frontend: Halaman blank / 404

```bash
# Cek apakah static files ada
ls /root/socsentinel/backend/static/index.html

# Jika tidak ada, rebuild frontend
cd /root/socsentinel/frontend
npm ci && npx vite build
cp -r dist/ ../backend/static/

# Restart backend
systemctl restart socsentinel
```

### ROCm: GPU tidak terdeteksi

```bash
# Cek ROCm installation
rocm-smi
rocminfo | grep -i "name"

# Jika tidak ada GPU:
# 1. Pastikan droplet size benar (gpu-mi300x1-192gb)
# 2. Coba destroy dan buat droplet baru
# 3. Contact AMD Dev Cloud support
```

### Port conflict: 8000 atau 8080 sudah dipakai

```bash
# Cek port yang dipakai
ss -tlnp | grep -E "8000|8080"

# Kill process yang blocking
kill $(lsof -t -i:8000)
kill $(lsof -t -i:8080)
```

---

## 📊 Quick Reference -- Command Cheatsheet

```bash
# ============ SSH ============
ssh root@DROPLET_IP

# ============ Cek GPU ============
rocm-smi
watch -n 1 rocm-smi

# ============ Install vLLM ============
pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/

# ============ Start vLLM (background) ============
screen -S vllm
python3 -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-14B \
  --host 0.0.0.0 --port 8000 \
  --max-model-len 8192 --gpu-memory-utilization 0.85 \
  --dtype auto --trust-remote-code
# Ctrl+A, D (detach)

# ============ Clone & Setup SOCsentinel ============
cd /root
git clone https://github.com/MIkhsanPasaribu/socsentinel.git
cd socsentinel/frontend && npm ci && npx vite build
cp -r dist/ ../backend/static/
cd ../backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: LLM_PROVIDER=vllm, VLLM_BASE_URL=http://localhost:8000/v1, PORT=8080

# ============ Start Backend (background) ============
screen -S backend
cd /root/socsentinel/backend && source .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
# Ctrl+A, D (detach)

# ============ Test ============
curl http://localhost:8000/v1/models          # vLLM
curl http://localhost:8080/health             # Backend
# Browser: http://DROPLET_IP:8080            # Frontend

# ============ Screen Management ============
screen -ls                # list sessions
screen -r vllm            # re-attach vLLM
screen -r backend         # re-attach backend

# ============ Firewall ============
ufw allow 8080/tcp
ufw allow 8000/tcp

# ============ Selesai? DESTROY DROPLET! ============
# https://devcloud.amd.com/gpus -> Destroy
```

---

**Selamat! SOCsentinel sekarang fully deployed dengan LLM sungguhan di AMD MI300X.** 🎉

> 💡 **Tip untuk Demo Hackathon**: Nyalakan droplet 20 menit sebelum demo. Model download pertama kali butuh ~10 menit, loading ~5 menit. Setelah itu, response sangat cepat (~1.5-4 detik per agent). Akses dashboard di `http://DROPLET_IP:8080`.
