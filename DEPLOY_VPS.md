# 🚀 SOCsentinel — VPS Deployment Guide (Ubuntu)

Tutorial lengkap deploy SOCsentinel (FastAPI + React) ke VPS Ubuntu 20.04/22.04/24.04.

---

## 📋 Prerequisites

| Requirement       | Minimum          | Recommended       |
| ----------------- | ---------------- | ----------------- |
| **OS**            | Ubuntu 20.04 LTS | Ubuntu 22.04 LTS  |
| **RAM**           | 2 GB             | 4 GB              |
| **CPU**           | 1 vCPU           | 2 vCPU            |
| **Disk**          | 20 GB            | 40 GB             |
| **Domain** (opsional) | —            | `socsentinel.yourdomain.com` |

---

## 🔧 Step 1: Setup Server & Dependencies

### 1.1 — SSH ke VPS

```bash
ssh root@YOUR_VPS_IP
```

### 1.2 — Update System

```bash
apt update && apt upgrade -y
```

### 1.3 — Install Required Packages

```bash
# Essentials
apt install -y git curl wget unzip build-essential software-properties-common

# Python 3.11
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-venv python3.11-dev

# Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Nginx (reverse proxy)
apt install -y nginx

# Certbot (SSL — opsional tapi recommended)
apt install -y certbot python3-certbot-nginx
```

### 1.4 — Verifikasi Instalasi

```bash
python3.11 --version   # Python 3.11.x
node --version          # v20.x.x
npm --version           # 10.x.x
nginx -v                # nginx/1.x.x
```

---

## 📦 Step 2: Clone & Setup Project

### 2.1 — Create App User (best practice: jangan pakai root)

```bash
useradd -m -s /bin/bash socsentinel
usermod -aG sudo socsentinel
su - socsentinel
```

### 2.2 — Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/socsentinel.git
cd socsentinel
```

> **Alternatif tanpa Git:** Upload file dari local pakai `scp`:
> ```bash
> # Dari local machine (bukan di VPS):
> scp -r ./socsentinel root@YOUR_VPS_IP:/home/socsentinel/
> ```

---

## ⚙️ Step 3: Setup Backend (FastAPI)

### 3.1 — Create Virtual Environment

```bash
cd ~/socsentinel/backend
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3.2 — Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> ⚠️ **WeasyPrint** butuh system dependencies:
> ```bash
> sudo apt install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2
> ```

### 3.3 — Configure Environment

```bash
cp .env.example .env
nano .env
```

Edit `.env` — ubah sesuai kebutuhan:

```env
# === Server ===
ENVIRONMENT=production
PORT=8000
FRONTEND_URL=http://YOUR_VPS_IP  # atau https://socsentinel.yourdomain.com
DEBUG=false

# === LLM Configuration ===
# Pakai "mock" untuk demo tanpa GPU, atau "vllm" kalau punya GPU server
LLM_PROVIDER=mock

# === Vector Database ===
CHROMA_PERSIST_DIR=./data/chroma_db
CHROMA_COLLECTION_NAME=mitre_attack

# === Embedding ===
EMBEDDING_MODEL=BAAI/bge-m3

# === Observability ===
LOG_LEVEL=INFO
```

### 3.4 — Ingest MITRE ATT&CK Data

```bash
python -m scripts.ingest_mitre
```

### 3.5 — Test Backend

```bash
# Quick test
python -m pytest tests/ -v

# Manual run test
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Buka browser: http://YOUR_VPS_IP:8000/health → harus return {"status": "ok"}
# Ctrl+C untuk stop
```

---

## 🎨 Step 4: Build Frontend (React)

### 4.1 — Install Dependencies

```bash
cd ~/socsentinel/frontend
npm install
```

### 4.2 — Configure API URL

Buat file `.env.production`:

```bash
nano .env.production
```

Isi:

```env
VITE_APP_NAME=SOCsentinel
VITE_API_URL=http://YOUR_VPS_IP/api/v1
VITE_WS_URL=ws://YOUR_VPS_IP/ws
```

> **Jika pakai domain + SSL**, ganti ke:
> ```env
> VITE_API_URL=https://socsentinel.yourdomain.com/api/v1
> VITE_WS_URL=wss://socsentinel.yourdomain.com/ws
> ```

### 4.3 — Build Production

```bash
npm run build
```

Output akan ada di folder `dist/`.

---

## 🔄 Step 5: Setup Systemd Service (Backend Auto-Start)

### 5.1 — Create Service File

```bash
sudo nano /etc/systemd/system/socsentinel-backend.service
```

Paste isi ini:

```ini
[Unit]
Description=SOCsentinel Backend (FastAPI)
After=network.target

[Service]
User=socsentinel
Group=socsentinel
WorkingDirectory=/home/socsentinel/socsentinel/backend
Environment="PATH=/home/socsentinel/socsentinel/backend/.venv/bin:/usr/bin"
ExecStart=/home/socsentinel/socsentinel/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 5.2 — Enable & Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable socsentinel-backend
sudo systemctl start socsentinel-backend

# Cek status
sudo systemctl status socsentinel-backend
```

### 5.3 — Cek Logs

```bash
sudo journalctl -u socsentinel-backend -f
```

---

## 🌐 Step 6: Configure Nginx (Reverse Proxy)

### 6.1 — Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/socsentinel
```

Paste isi ini:

```nginx
server {
    listen 80;
    server_name YOUR_VPS_IP;  # Ganti dengan domain jika ada: socsentinel.yourdomain.com

    # Frontend (React static files)
    root /home/socsentinel/socsentinel/frontend/dist;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 256;

    # API Proxy → FastAPI backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support (critical for real-time streaming)
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # Health endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
    }

    # OpenAPI docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host $host;
    }

    # React SPA — semua route lain ke index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 6.2 — Enable Site

```bash
sudo ln -sf /etc/nginx/sites-available/socsentinel /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Hapus default site

# Test config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## 🔒 Step 7: SSL Certificate (Opsional — Recommended)

> Skip step ini jika belum punya domain. Bisa pakai IP langsung.

### 7.1 — Point Domain ke VPS

Di DNS provider kamu, tambahkan A record:
```
socsentinel.yourdomain.com → YOUR_VPS_IP
```

### 7.2 — Install SSL dengan Certbot

```bash
sudo certbot --nginx -d socsentinel.yourdomain.com
```

Ikuti prompt:
1. Masukkan email
2. Agree to terms
3. Pilih redirect HTTP → HTTPS

Certbot akan otomatis update Nginx config.

### 7.3 — Auto-Renew

```bash
sudo certbot renew --dry-run
```

---

## 🔥 Step 8: Firewall

```bash
# Buka port yang dibutuhkan
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'  # port 80 + 443
sudo ufw enable

# Verifikasi
sudo ufw status
```

> **JANGAN** buka port 8000 ke publik. Backend hanya accessible via Nginx proxy.

---

## ✅ Step 9: Verifikasi Deployment

### 9.1 — Test Endpoints

```bash
# Health check
curl http://YOUR_VPS_IP/health

# API stats
curl http://YOUR_VPS_IP/api/v1/pipeline/stats

# Generate alert
curl -X POST http://YOUR_VPS_IP/api/v1/alerts/generate \
  -H "Content-Type: application/json" \
  -d '{"scenario": "brute_force"}'
```

### 9.2 — Buka di Browser

```
http://YOUR_VPS_IP
```

Kamu harus melihat dashboard SOCsentinel lengkap.

---

## 🔄 Step 10: Update / Redeploy

Setiap kali ada perubahan code:

```bash
# SSH ke VPS
ssh socsentinel@YOUR_VPS_IP

# Pull latest code
cd ~/socsentinel
git pull origin main

# Update backend
cd backend
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart socsentinel-backend

# Update frontend
cd ../frontend
npm install
npm run build

# Nginx otomatis serve file baru (static files)
```

---

## 🛠️ Troubleshooting

### Backend tidak start

```bash
sudo journalctl -u socsentinel-backend -n 50 --no-pager
```

### Nginx error

```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### SSE streaming tidak jalan

Pastikan config Nginx ada:
```nginx
proxy_buffering off;
proxy_cache off;
```

### Port 8000 already in use

```bash
sudo lsof -i :8000
sudo kill -9 <PID>
sudo systemctl restart socsentinel-backend
```

### Permission denied

```bash
sudo chown -R socsentinel:socsentinel /home/socsentinel/socsentinel
```

---

## 📊 Arsitektur Production

```
┌─────────────────────────────────────────────┐
│                    Internet                  │
└────────────────────┬────────────────────────┘
                     │ :80 / :443
┌────────────────────▼────────────────────────┐
│              Nginx (Reverse Proxy)           │
│  ┌─────────────────┬──────────────────────┐ │
│  │  /api/* /health  │  /* (static files)   │ │
│  │  → proxy :8000   │  → frontend/dist/    │ │
│  └────────┬────────┴──────────────────────┘ │
└───────────┼─────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────┐
│         FastAPI Backend (:8000)              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │  SQLite   │  │ ChromaDB │  │ 9 Agents  │ │
│  │  (audit)  │  │  (RAG)   │  │  (LLM)    │ │
│  └──────────┘  └──────────┘  └───────────┘ │
└─────────────────────────────────────────────┘
```

---

## ⏱️ Quick Deploy (Copy-Paste One-Liner)

Untuk yang mau cepat, jalankan semua sekaligus setelah clone:

```bash
# Backend
cd ~/socsentinel/backend && \
python3.11 -m venv .venv && \
source .venv/bin/activate && \
pip install -r requirements.txt && \
cp .env.example .env && \
python -m scripts.ingest_mitre

# Frontend
cd ~/socsentinel/frontend && \
npm install && \
npm run build

echo "✅ Build selesai. Setup systemd + nginx sesuai guide di atas."
```

---

**Selamat! SOCsentinel sekarang live di VPS kamu.** 🎉
