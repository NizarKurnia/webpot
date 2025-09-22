WebPot

WebPot adalah honeypot sederhana berbasis Python yang digunakan untuk mempelajari serangan web dan menyimpan payload serangan yang dilakukan di log.

Cara Install & Setup

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

**Cara Menggunakan**
- Pertama kita masukan link website yang mau kita salin ke cloner.py
- Kedua kita jalankan cloner.py
- Ketiga kita buka index.html di fake_web lalu kita ubah (form action=URL) dibagian login menjadi "/"
- Keempat Jalankan server 
- Kelima klik link local server
- Keenam tes masukan kredensial
- Ketujuh lihat log di logs/honeypot.JSON

**Struktur Project**
- trap_server.py → file utama untuk menjalankan honeypot
- cloner.py → script untuk meng-clone halaman target
- fake_web/ → hasil clone halaman target
- requirements.txt → daftar library yang diperlukan

**Notice**
Jika ingin response honeypot muncul di log jangan lupa ubah link (form action="URL target") dibagian form login menjadi "/"

**Catatan**
- Gunakan hanya untuk pembelajaran / testing legal
- Disarankan menjalankan di environment terisolasi (misal VM)
