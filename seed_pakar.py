import mysql.connector
from werkzeug.security import generate_password_hash

# --- KONFIGURASI ---
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "",
    'database': "db_sistem_pakar"  # Pastikan ini nama database baru Anda
}

KRITERIA_DATA = [
    {'kode': 'PENGHASILAN', 'nama': 'Penghasilan Orang Tua (Juta Rp)', 'tipe': 'input'},
    {'kode': 'NILAI', 'nama': 'Nilai Rata-Rata Rapor', 'tipe': 'input'},
    {'kode': 'TANGGUNGAN', 'nama': 'Jumlah Tanggungan Keluarga', 'tipe': 'input'},
    {'kode': 'PRESTASI', 'nama': 'Poin Prestasi Non-Akademik', 'tipe': 'input'},
    {'kode': 'KELAYAKAN', 'nama': 'Tingkat Kelayakan Beasiswa', 'tipe': 'output'}
]

HIMPUNAN_DATA = {
    'PENGHASILAN': [
        {'nama': 'Rendah', 'nilai': [0, 0, 1, 2.5]},
        {'nama': 'Sedang', 'nilai': [1.5, 3, 4, 5.5]},
        {'nama': 'Tinggi', 'nilai': [4.5, 6, 100, 100]}
    ],
    'NILAI': [
        {'nama': 'Rendah', 'nilai': [0, 0, 50, 65]},
        {'nama': 'Sedang', 'nilai': [60, 70, 80, 85]},
        {'nama': 'Tinggi', 'nilai': [80, 90, 100, 100]}
    ],
    'TANGGUNGAN': [
        {'nama': 'Sedikit', 'nilai': [0, 0, 1, 3]},
        {'nama': 'Sedang', 'nilai': [2, 3, 4, 6]},
        {'nama': 'Banyak', 'nilai': [5, 6, 10, 10]}
    ],
    'PRESTASI': [
        {'nama': 'Rendah', 'nilai': [0, 0, 10, 30]},
        {'nama': 'Sedang', 'nilai': [20, 40, 60, 70]},
        {'nama': 'Tinggi', 'nilai': [60, 80, 100, 100]}
    ],
    'KELAYAKAN': [
        {'nama': 'Tidak Layak', 'nilai': [0, 0, 40, 55]},
        {'nama': 'Dipertimbangkan', 'nilai': [50, 60, 70, 80]},
        {'nama': 'Layak', 'nilai': [75, 85, 100, 100]}
    ]
}

ATURAN_DATA = [
    {'nama': 'ER-NT', 'IF': [('PENGHASILAN','Rendah'), ('NILAI','Tinggi')], 'THEN': ('KELAYAKAN','Layak')},
    {'nama': 'ER-TB', 'IF': [('PENGHASILAN','Rendah'), ('TANGGUNGAN','Banyak')], 'THEN': ('KELAYAKAN','Layak')},
    {'nama': 'ES-NT', 'IF': [('PENGHASILAN','Sedang'), ('NILAI','Tinggi')], 'THEN': ('KELAYAKAN','Layak')},
    {'nama': 'ES-ND', 'IF': [('PENGHASILAN','Sedang'), ('NILAI','Rendah')], 'THEN': ('KELAYAKAN','Dipertimbangkan')},
    {'nama': 'ET-NR', 'IF': [('PENGHASILAN','Tinggi'), ('NILAI','Rendah')], 'THEN': ('KELAYAKAN','Tidak Layak')},
    {'nama': 'Default-NS', 'IF': [('NILAI','Sedang')], 'THEN': ('KELAYAKAN','Dipertimbangkan')}
]

def setup_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print(f"Berhasil terhubung ke database '{DB_CONFIG['database']}'.")

        # 1. Buat user admin
        print("\nMembuat user admin...")
        cursor.execute("DELETE FROM users WHERE username = 'admin'")
        admin_pass_hash = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO users (nama_lengkap, username, password, peran) VALUES (%s, %s, %s, %s)",
            ('Administrator', 'admin', admin_pass_hash, 'admin')
        )
        print("  - User 'admin' dengan password 'admin123' berhasil dibuat.")

        # 2. Masukkan Kriteria
        print("\nMemasukkan kriteria...")
        kriteria_ids = {}
        for k in KRITERIA_DATA:
            cursor.execute("INSERT INTO kriteria (kode_kriteria, nama_kriteria, tipe) VALUES (%s, %s, %s)",
                         (k['kode'], k['nama'], k['tipe']))
            k_id = cursor.lastrowid
            kriteria_ids[k['kode']] = k_id
            print(f"  - Kriteria '{k['nama']}' ditambahkan.")
        
        # 3. Masukkan Himpunan Fuzzy
        print("\nMemasukkan himpunan fuzzy...")
        himpunan_ids = {}
        for kode_kriteria, himpunan_list in HIMPUNAN_DATA.items():
            k_id = kriteria_ids[kode_kriteria]
            for h in himpunan_list:
                cursor.execute(
                    "INSERT INTO himpunan_fuzzy (kriteria_id, nama_himpunan, nilai1, nilai2, nilai3, nilai4) VALUES (%s, %s, %s, %s, %s, %s)",
                    (k_id, h['nama'], h['nilai'][0], h['nilai'][1], h['nilai'][2], h['nilai'][3])
                )
                h_id = cursor.lastrowid
                himpunan_ids[(kode_kriteria, h['nama'])] = h_id
                print(f"  - Himpunan '{h['nama']}' untuk '{kode_kriteria}' ditambahkan.")

        # 4. Masukkan Aturan Fuzzy
        print("\nMemasukkan aturan fuzzy...")
        for a in ATURAN_DATA:
            cursor.execute("INSERT INTO aturan_fuzzy (nama_aturan) VALUES (%s)", (a['nama'],))
            aturan_id = cursor.lastrowid
            for cond_k_kode, cond_h_nama in a['IF']:
                himpunan_id = himpunan_ids[(cond_k_kode, cond_h_nama)]
                cursor.execute("INSERT INTO kondisi_aturan (aturan_id, himpunan_id) VALUES (%s, %s)", (aturan_id, himpunan_id))
            then_k_kode, then_h_nama = a['THEN']
            himpunan_id = himpunan_ids[(then_k_kode, then_h_nama)]
            cursor.execute("INSERT INTO konsekuen_aturan (aturan_id, himpunan_id) VALUES (%s, %s)", (aturan_id, himpunan_id))
            print(f"  - Aturan '{a['nama']}' ditambahkan.")

        conn.commit()
        print("\nProses setup database selesai!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    setup_database()