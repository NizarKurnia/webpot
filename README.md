## WebPot

WebPot adalah honeypot sederhana berbasis Python yang digunakan untuk mempelajari serangan web dan menyimpan payload serangan yang dilakukan di log.
Project ini merupakan hasil modifikasi dari [WebTrap](https://github.com/IllusiveNetworks-Labs/WebTrap), dengan beberapa fitur tambahan dan penyesuaian.

## Cara Install & Setup

**Clone Repository**
```bash
git clone https://github.com/usernamekamu/webpot.git
cd webpot
```

**Buat Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**Install Dependencies**
```bash
pip install -r requirements.txt
```

**Clone Web**
```bash
python cloner.py
```

**Jalankan Server**
```bash
python trap_server.py
```

## Cara Menggunakan
- Siapkan `config.json` untuk mengatur `target_url`, `webroot`, `honeypot_log`, dan `port`. 
- Clone halaman target menggunakan `cloner.py`. Contoh:

```powershell
python .\cloner.py --url "https://example.com" --out fake_web
```
Atau
``` bash
nano config.json
```

- Jalankan honeypot server:

```
python .\trap_server.py
```

- Buka browser ke `http://localhost:<port>/` (default `5050`, atau sesuai `config.json`) dan gunakan antarmuka yang sudah dikloning.
- Masukkan kredensial pada form untuk menghasilkan entri log.
- Lihat log event di file log yang dikonfigurasi (`logs/honeypot.json` secara default). Logs tersimpan sebagai JSON Lines (satu objek JSON per baris) untuk kemudahan pemrosesan.

## Struktur Project
- trap_server.py → file utama untuk menjalankan honeypot
- cloner.py → script untuk meng-clone halaman target
- fake_web/ → hasil clone halaman target
- requirements.txt → daftar library yang diperlukan

## Notice
- `cloner.py` sudah otomatis mengubah `form action` menjadi `/`; Tidak perlu mengedit `index.html` secara manual.
- Log disimpan sebagai JSON Lines di file yang dikonfigurasi (`logs/honeypot.json` secara default).

## Catatan
- Gunakan hanya untuk pembelajaran / testing legal

---

## ⚖️ License

WebPot berisi kode dari *WebTrap*, yang dilisensikan di bawah **BSD-3-Clause License**.  
Lihat [LICENSE](LICENSE) untuk detail lengkap.

---

## 🙏 Acknowledgements

- [WebTrap](https://github.com/IllusiveNetworks-Labs/WebTrap) — project asli yang menjadi dasar WebPot.
- Semua kontributor open-source yang membantu membangun ekosistem ini.

