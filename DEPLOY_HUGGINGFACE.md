# 🚀 Deploying SOCsentinel to Hugging Face Spaces

Tutorial ini menjelaskan cara meng-host **SOCsentinel** (UI & Backend Orchestrator) di Hugging Face Spaces sebagai platform demo utama untuk AMD Developer Hackathon.

## 🏗️ Architecture Overview

Dalam setup produksi untuk hackathon, kita menggunakan arsitektur hybrid:
1. **AMD Developer Cloud**: Menjalankan LLM (Qwen3) menggunakan vLLM pada GPU MI300X (High Performance).
2. **Hugging Face Spaces**: Menjalankan aplikasi SOCsentinel (React + FastAPI) sebagai antarmuka publik yang dapat diakses juri.

---

## 📋 Prerequisites

1. Akun [Hugging Face](https://huggingface.co/).
2. Akses ke [AMD Developer Cloud](https://cloud.amd.com/) (untuk mendapatkan API endpoint LLM).
3. Docker Desktop (opsional, untuk testing lokal).

---

## 🛠️ Step-by-Step Setup

### 1. Create a New Space
1. Pergi ke [huggingface.co/new-space](https://huggingface.co/new-space).
2. **Owner**: Pilih akun Anda atau organisasi tim Anda.
3. **Space Name**: `socsentinel`.
4. **SDK**: Pilih **Docker**.
5. **Docker Template**: Pilih **Blank**.
6. **Hardware**: Pilih **CPU Basic** (Gratis) atau **GPU** (jika mendapatkan grant dari panitia).
7. **Privacy**: **Public** (agar juri bisa melihat).

### 2. Configure Secrets (PENTING)
Agar aplikasi bisa terhubung ke model AI dan database, Anda harus mengatur Environment Variables di Settings Space:
1. Buka tab **Settings** di Space Anda.
2. Cari bagian **Variables and secrets**.
3. Tambahkan "New secret" untuk variabel berikut:

| Variable | Value (Contoh) | Deskripsi |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `vllm` | Gunakan `vllm` untuk produksi. |
| `VLLM_BASE_URL` | `http://<IP_AMD_CLOUD>:8000/v1` | URL API dari AMD Developer Cloud. |
| `ENVIRONMENT` | `production` | Mengaktifkan mode produksi. |
| `FRONTEND_URL` | `*` | Mengizinkan akses CORS dari mana saja. |
| `CHROMA_PERSIST_DIR` | `./data/chroma_db` | Lokasi database vector. |

### 3. Push Code to Space
Gunakan Git untuk mengupload kode Anda ke Hugging Face:

```bash
# Clone repo Space Anda (ganti USERNAME)
git clone https://huggingface.co/spaces/USERNAME/socsentinel
cd socsentinel

# Copy semua file project SOCsentinel ke folder ini
# Pastikan Dockerfile berada di root folder Space

# Commit dan Push
git add .
git commit -m "Deploy SOCsentinel to HF Spaces"
git push
```

---

## 🐳 Mengapa Dockerfile Ini Berfungsi?

Dockerfile di project ini sudah dioptimasi untuk HF Spaces:
1. **Multi-stage Build**: Membangun frontend React menggunakan Node.js, lalu memindahkannya ke container Python.
2. **Static Serving**: Backend FastAPI dikonfigurasi untuk menyajikan file statis React dari folder `/static`.
3. **Port 7860**: Menggunakan port standar Hugging Face.
4. **Non-root User**: Berjalan dengan `appuser` (UID 1000) sesuai aturan keamanan HF.

---

## 🔍 Troubleshooting

- **Log Build Error**: Cek tab **Logs** di Space Anda jika proses building gagal.
- **Connection Refused**: Pastikan `VLLM_BASE_URL` mengarah ke IP publik server AMD Cloud Anda dan port (biasanya 8000) sudah dibuka di firewall.
- **Empty Screen**: Jika UI tidak muncul, pastikan build frontend berhasil dan file `index.html` ada di folder `/app/static` di dalam container.

---

## 🏆 Tips untuk Hackathon
Hugging Face memberikan poin tambahan jika Space Anda mendapatkan banyak "Like". Pastikan untuk mengisi **README.md** (yang merupakan file Metadata Space) dengan deskripsi project yang menarik dan instruksi penggunaan yang jelas.
