# Sistem Pendukung Keputusan Kelayakan Beasiswa (Logika Fuzzy)

Aplikasi web ini dibangun untuk menentukan kelayakan seorang mahasiswa dalam mendapatkan beasiswa menggunakan gabungan dua metode: Logika Fuzzy untuk skoring kuantitatif dan Sistem Pakar (Expert System) untuk memberikan rekomendasi kualitatif berdasarkan hasil skor fuzzy.

## Screenshot Aplikasi
*(Sangat disarankan untuk menaruh beberapa gambar tampilan aplikasi di sini. Tunjukkan halaman login, dashboard admin, dan halaman pengecekan mahasiswa)*

![Halaman Login](LINK_GAMBAR_LOGIN_DISINI)
![Dashboard Admin](LINK_GAMBAR_ADMIN_DISINI)
![Halaman Pengecekan](LINK_GAMBAR_MAHASISWA_DISINI)

## Teknologi yang Digunakan
* **Framework Backend:** Flask
* **Database:** MySQL
* **Manajemen Login:** Flask-Login
* **Library Python:**
    * `mysql-connector-python` untuk interaksi database.
    * `numpy` untuk kalkulasi fuzzy.
    * `werkzeug` untuk hashing password.
* **Frontend:** Bootstrap 5

## Struktur Proyek
* `app.py`: File utama aplikasi Flask yang mengatur semua rute (URL) dan logika bisnis.
* `fuzzy_engine.py`: Berisi semua fungsi untuk logika fuzzy, mulai dari fuzzifikasi, inferensi, hingga defuzzifikasi.
* `expert_system.py`: Berisi basis pengetahuan (knowledge base) dan aturan-aturan kualitatif untuk memberikan rekomendasi akhir.
* `schema_sistem_pakar.sql`: Skema lengkap untuk membuat struktur database.
* `seed_pakar.py`: Skrip untuk mengisi database dengan data awal (kriteria, himpunan, aturan, dan user admin).
* `requirements.txt`: Daftar semua pustaka Python yang dibutuhkan oleh proyek.

## Cara Instalasi & Konfigurasi
Berikut adalah langkah-langkah untuk menjalankan proyek ini di lingkungan lokal.

#### 1. Prasyarat
* Python 3.x
* Server Database MySQL (seperti XAMPP, WAMP, atau instalasi MySQL langsung)

#### 2. Clone Repository
```bash
git clone [https://github.com/Aedenx/Beasiswa_Fuzzy.git](https://github.com/Aedenx/Beasiswa_Fuzzy.git)
cd Beasiswa_Fuzzy
