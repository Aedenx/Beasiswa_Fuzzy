# Sistem Pendukung Keputusan Kelayakan Beasiswa (Logika Fuzzy)

Aplikasi web ini dibangun untuk menentukan kelayakan seorang mahasiswa dalam mendapatkan beasiswa menggunakan gabungan dua metode: Logika Fuzzy untuk skoring kuantitatif dan Sistem Pakar (Expert System) untuk memberikan rekomendasi kualitatif berdasarkan hasil skor fuzzy.

## Screenshot Aplikasi
*(Sangat disarankan untuk menaruh beberapa gambar tampilan aplikasi di sini. Tunjukkan halaman login, dashboard admin, dan halaman pengecekan mahasiswa)*

![Halaman Pengecekan]![Image](https://github.com/user-attachments/assets/9387fb52-f61f-48d1-85f3-a102f0fc6079)
![Dashboard Admin]![Image](https://github.com/user-attachments/assets/3c08f264-50b9-49dc-9ff6-1e056943934f)
![Halaman Login]![Image](https://github.com/user-attachments/assets/267ded42-9012-4a74-88d0-d69d80c0bd91)


Demo Video https://drive.google.com/file/d/1XvcIHm5cAhbDQ1y8Kc6Sbs_6HLiCosBB/view?usp=drive_link

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
