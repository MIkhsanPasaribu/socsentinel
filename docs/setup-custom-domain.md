# Tutorial: Menghubungkan Domain Namecheap ke SOCsentinel (AMD DevCloud)

Panduan ini menjelaskan cara mengonfigurasi domain Anda dari **Namecheap** agar mengarah ke aplikasi SOCsentinel yang berjalan di server AMD DevCloud (IP: `134.199.194.39`).

---

## Langkah 1: Konfigurasi DNS di Namecheap

1. Login ke akun [Namecheap](https://www.namecheap.com/).
2. Masuk ke **Dashboard** > **Domain List**.
3. Klik tombol **Manage** di samping nama domain Anda.
4. Klik tab **Advanced DNS**.
5. Tambahkan dua baris **Host Records** berikut:

| Type | Host | Value | TTL |
| :--- | :--- | :--- | :--- |
| **A Record** | `@` | `134.199.194.39` | Automatic |
| **A Record** | `www` | `134.199.194.39` | Automatic |

*Catatan: Jika sudah ada record tipe CNAME atau A yang lama, hapus terlebih dahulu.*

---

## Langkah 2: Install Nginx di Server AMD DevCloud

Aplikasi Anda saat ini berjalan di port `8080`. Kita akan menggunakan Nginx sebagai *Reverse Proxy* agar domain bisa diakses melalui port standar HTTP (80) dan HTTPS (443).

1. Masuk ke terminal SSH server Anda.
2. Install Nginx:
   ```bash
   sudo apt update
   sudo apt install nginx -y
   ```

---

## Langkah 3: Konfigurasi Nginx untuk Domain

1. Buat file konfigurasi baru (ganti `domainanda.com` dengan domain asli Anda):
   ```bash
   sudo nano /etc/nginx/sites-available/socsentinel
   ```
2. Tempelkan konfigurasi berikut:
   ```nginx
   server {
       listen 80;
       server_name domainanda.com www.domainanda.com;

       location / {
           proxy_pass http://127.0.0.1:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # Penting untuk SSE (Server-Sent Events) di Pipeline
           proxy_set_header Connection '';
           proxy_http_version 1.1;
           chunked_transfer_encoding off;
           proxy_buffering off;
           proxy_cache off;
       }
   }
   ```
3. Aktifkan konfigurasi dan restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/socsentinel /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## Langkah 4: Pasang SSL Gratis (HTTPS) dengan Certbot

Sangat penting menggunakan HTTPS untuk kredibilitas aplikasi hackathon Anda.

1. Install Certbot:
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   ```
2. Jalankan perintah SSL (ikuti instruksi di layar, masukkan email dan pilih 'Yes'):
   ```bash
   sudo certbot --nginx -d domainanda.com -d www.domainanda.com
   ```
3. Certbot akan otomatis mengubah file Nginx Anda menjadi HTTPS.

---

## Langkah 5: Update Konfigurasi Backend (Opsional)

Jika Anda menggunakan domain baru, pastikan aturan CORS di backend mengizinkan domain tersebut.

1. Buka file `.env` di folder `backend`:
   ```bash
   nano /root/socsentinel/backend/.env
   ```
2. Pastikan `FRONTEND_URL` mengarah ke domain Anda:
   ```env
   FRONTEND_URL=https://domainanda.com
   ```
3. Restart service backend:
   ```bash
   sudo systemctl restart socsentinel
   ```

---

## Ringkasan Akhir
Sekarang aplikasi Anda dapat diakses di: `https://domainanda.com` tanpa perlu mengetikkan `:8080` lagi.

> [!TIP]
> Perubahan DNS Namecheap biasanya memakan waktu 5-30 menit untuk menyebar (propagate). Jika belum bisa diakses, tunggu sejenak atau cek di [DNSChecker.org](https://dnschecker.org/).
