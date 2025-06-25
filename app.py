import mysql.connector
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for, flash, jsonify, abort)
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import (Flask, render_template, request, redirect, url_for, flash, jsonify, abort)
from functools import wraps
from expert_system import KnowledgeBase

# Import class dari file Anda, bukan instance global
from expert_system import KnowledgeBase, InferenceEngine
# Import semua fungsi yang dibutuhkan
from fuzzy_engine import load_fuzzy_model, run_inference_engine, generate_chart_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci-rahasia-yang-super-aman-dan-sulit-ditebak-12345'

# Konfigurasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# ... (sisa konfigurasi login manager)

# Fungsi helper & model User (biarkan sama seperti yang Anda punya)
# Di dalam app.py
def get_db_connection():
    try:
        # UBAH BARIS INI
        return mysql.connector.connect(host="localhost", user="root", password="", database="db_sistem_pakar")
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

class User(UserMixin):
    # ... (kode class User Anda)
    def __init__(self, id, username, peran, nama_lengkap):
        self.id = id
        self.username = username
        self.peran = peran
        self.nama_lengkap = nama_lengkap

@login_manager.user_loader
def load_user(user_id):
    # ... (kode load_user Anda)
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return User(id=user_data['id'], username=user_data['username'], peran=user_data['peran'], nama_lengkap=user_data.get('nama_lengkap', user_data['username']))
    return None
def admin_required(f):
    """Decorator untuk memastikan hanya admin yang bisa mengakses rute."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.peran != 'admin':
            return abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        peran = request.form.get('peran')

        if not username or not password or not peran:
            flash('Username, Password, dan Peran harus diisi!', 'warning')
            return redirect(url_for('login'))

        conn = get_db_connection()
        if not conn:
            flash('Koneksi ke database gagal, silakan coba lagi nanti.', 'danger')
            return render_template('login.html')

        cursor = conn.cursor(dictionary=True)
        # UBAH QUERY untuk memeriksa username DAN peran
        cursor.execute('SELECT * FROM users WHERE username = %s AND peran = %s', (username, peran))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        # Logika Pengecekan (sisa kode tetap sama)
        if user_data:
            if check_password_hash(user_data['password'], password):
                user = User(
                    id=user_data['id'],
                    username=user_data['username'],
                    peran=user_data['peran'],
                    nama_lengkap=user_data.get('nama_lengkap')
                )
                login_user(user)
                flash('Login berhasil!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Password salah untuk peran yang dipilih.', 'danger')
        else:
            # Pesan error diubah agar lebih spesifik
            flash(f'Username tidak ditemukan untuk peran {peran}.', 'danger')
        
        return redirect(url_for('login'))

    # Untuk method GET, tampilkan halaman login
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Menangani logika untuk registrasi user mahasiswa baru."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Ambil data dari form
        nama_lengkap = request.form.get('nama')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validasi dasar
        if not nama_lengkap or not username or not password or not confirm_password:
            flash('Semua kolom wajib diisi!', 'warning')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Password dan Konfirmasi Password tidak cocok!', 'warning')
            return redirect(url_for('register'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Cek apakah username sudah ada
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username sudah terdaftar, silakan gunakan username lain.', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('register'))

        # Hash password sebelum disimpan
        password_hash = generate_password_hash(password)

        # Simpan user baru dengan peran 'mahasiswa'
        try:
            cursor.execute(
                "INSERT INTO users (nama_lengkap, username, password, peran) VALUES (%s, %s, %s, %s)",
                (nama_lengkap, username, password_hash, 'mahasiswa')
            )
            conn.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Terjadi error pada database: {err}", "danger")
            return redirect(url_for('register'))
        finally:
            cursor.close()
            conn.close()

    # Untuk method GET, tampilkan halaman registrasi
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    if current_user.peran == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('dashboard_mahasiswa'))

# === RUTE-RUTE ADMIN (TIDAK PERLU DIUBAH) ===
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(id) as total FROM users WHERE peran = 'mahasiswa'")
    total_mahasiswa = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(id) as total FROM kriteria")
    total_kriteria = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(id) as total FROM aturan_fuzzy")
    total_aturan_fuzzy = cursor.fetchone()['total']

    cursor.close()
    conn.close()

    kb = KnowledgeBase()
    total_aturan_pakar = len(kb.rules)

    stats = {
        'total_mahasiswa': total_mahasiswa,
        'total_kriteria': total_kriteria,
        'total_aturan_pakar': total_aturan_pakar
    }

    # Variabel pendaftar_terbaru sudah dihapus dari sini
    return render_template('admin/dashboard.html', stats=stats)

def admin_required(f):
    """Decorator untuk memastikan hanya admin yang bisa mengakses rute."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.peran != 'admin':
            return abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# === RUTE-RUTE MANAJEMEN ADMIN ===
# --- CRUD Pengguna Mahasiswa ---

@app.route('/admin/pengguna/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_pengguna_tambah():
    if request.method == 'POST':
        nama_lengkap = request.form.get('nama_lengkap')
        username = request.form.get('username')
        password = request.form.get('password')

        if not nama_lengkap or not username or not password:
            flash('Semua kolom wajib diisi untuk pengguna baru!', 'warning')
            return redirect(url_for('admin_pengguna_tambah'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('Username sudah digunakan.', 'danger')
        else:
            password_hash = generate_password_hash(password)
            cursor.execute("INSERT INTO users (nama_lengkap, username, password, peran) VALUES (%s, %s, %s, 'mahasiswa')", 
                           (nama_lengkap, username, password_hash))
            conn.commit()
            flash('Mahasiswa baru berhasil ditambahkan!', 'success')
            return redirect(url_for('admin_daftar_pengguna'))
        cursor.close()
        conn.close()

    return render_template('admin/pengguna_form.html', pengguna=None)


@app.route('/admin/pengguna/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_pengguna_edit(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nama_lengkap = request.form.get('nama_lengkap')
        username = request.form.get('username')
        password = request.form.get('password')

        # Cek duplikasi username (jika username diubah)
        cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", (username, user_id))
        if cursor.fetchone():
            flash('Username sudah digunakan oleh pengguna lain.', 'danger')
        else:
            if password:
                # Jika password diisi, update password
                password_hash = generate_password_hash(password)
                cursor.execute("UPDATE users SET nama_lengkap=%s, username=%s, password=%s WHERE id=%s", 
                               (nama_lengkap, username, password_hash, user_id))
            else:
                # Jika password kosong, jangan update password
                cursor.execute("UPDATE users SET nama_lengkap=%s, username=%s WHERE id=%s", 
                               (nama_lengkap, username, user_id))
            conn.commit()
            flash('Data mahasiswa berhasil diperbarui!', 'success')
            return redirect(url_for('admin_daftar_pengguna'))
    
    cursor.execute("SELECT id, nama_lengkap, username FROM users WHERE id = %s", (user_id,))
    pengguna = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin/pengguna_form.html', pengguna=pengguna)


@app.route('/admin/pengguna/hapus/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_pengguna_hapus(user_id):
    # Tambahan keamanan: pastikan hanya bisa menghapus mahasiswa
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s AND peran = 'mahasiswa'", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Akun mahasiswa berhasil dihapus.', 'success')
    return redirect(url_for('admin_daftar_pengguna'))

# --- Manajemen Kriteria ---
@app.route('/admin/kriteria', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_kriteria():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        kode = request.form.get('kode_kriteria').upper()
        nama = request.form.get('nama_kriteria')
        tipe = request.form.get('tipe')
        
        try:
            cursor.execute("INSERT INTO kriteria (kode_kriteria, nama_kriteria, tipe) VALUES (%s, %s, %s)", (kode, nama, tipe))
            conn.commit()
            flash('Kriteria baru berhasil ditambahkan!', 'success')
            load_fuzzy_model() # Muat ulang model fuzzy
        except mysql.connector.Error as err:
            flash(f'Gagal menambahkan kriteria: {err}', 'danger')
        
        cursor.close()
        conn.close()
        return redirect(url_for('admin_kriteria'))

    cursor.execute("SELECT * FROM kriteria ORDER BY id")
    daftar_kriteria = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/kriteria.html', daftar_kriteria=daftar_kriteria)

@app.route('/admin/kriteria/edit/<int:kriteria_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_kriteria_edit(kriteria_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        kode = request.form.get('kode_kriteria').upper()
        nama = request.form.get('nama_kriteria')
        tipe = request.form.get('tipe')
        cursor.execute("UPDATE kriteria SET kode_kriteria=%s, nama_kriteria=%s, tipe=%s WHERE id=%s", (kode, nama, tipe, kriteria_id))
        conn.commit()
        flash('Kriteria berhasil diperbarui!', 'success')
        load_fuzzy_model()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_kriteria'))
    
    cursor.execute("SELECT * FROM kriteria WHERE id = %s", (kriteria_id,))
    kriteria = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin/kriteria_edit.html', kriteria=kriteria)

@app.route('/admin/kriteria/hapus/<int:kriteria_id>', methods=['POST'])
@login_required
@admin_required
def admin_kriteria_hapus(kriteria_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM kriteria WHERE id = %s", (kriteria_id,))
        conn.commit()
        flash('Kriteria berhasil dihapus.', 'success')
        load_fuzzy_model()
    except mysql.connector.Error as err:
        flash(f'Gagal menghapus kriteria. Pastikan tidak ada himpunan atau aturan yang terkait. Error: {err}', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('admin_kriteria'))

# --- Manajemen Himpunan Fuzzy ---
@app.route('/admin/himpunan_fuzzy/<int:kriteria_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_himpunan_fuzzy(kriteria_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nama = request.form.get('nama_himpunan')
        n1 = request.form.get('nilai1')
        n2 = request.form.get('nilai2')
        n3 = request.form.get('nilai3')
        n4 = request.form.get('nilai4')
        cursor.execute("INSERT INTO himpunan_fuzzy (kriteria_id, nama_himpunan, nilai1, nilai2, nilai3, nilai4) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (kriteria_id, nama, n1, n2, n3, n4))
        conn.commit()
        flash('Himpunan fuzzy baru berhasil ditambahkan!', 'success')
        load_fuzzy_model()
        return redirect(url_for('admin_himpunan_fuzzy', kriteria_id=kriteria_id))

    cursor.execute("SELECT * FROM kriteria WHERE id = %s", (kriteria_id,))
    kriteria = cursor.fetchone()
    cursor.execute("SELECT * FROM himpunan_fuzzy WHERE kriteria_id = %s ORDER BY nilai1", (kriteria_id,))
    daftar_himpunan = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/himpunan_fuzzy.html', kriteria=kriteria, daftar_himpunan=daftar_himpunan)

@app.route('/admin/himpunan/edit/<int:himpunan_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_himpunan_edit(himpunan_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        nama = request.form.get('nama_himpunan')
        n1 = request.form.get('nilai1')
        n2 = request.form.get('nilai2')
        n3 = request.form.get('nilai3')
        n4 = request.form.get('nilai4')
        cursor.execute("UPDATE himpunan_fuzzy SET nama_himpunan=%s, nilai1=%s, nilai2=%s, nilai3=%s, nilai4=%s WHERE id=%s", 
                       (nama, n1, n2, n3, n4, himpunan_id))
        conn.commit()
        
        cursor.execute("SELECT kriteria_id FROM himpunan_fuzzy WHERE id = %s", (himpunan_id,))
        kriteria_id = cursor.fetchone()['kriteria_id']
        
        flash('Himpunan fuzzy berhasil diperbarui!', 'success')
        load_fuzzy_model()
        return redirect(url_for('admin_himpunan_fuzzy', kriteria_id=kriteria_id))

    cursor.execute("SELECT h.*, k.nama_kriteria, k.id as kriteria_id FROM himpunan_fuzzy h JOIN kriteria k ON h.kriteria_id = k.id WHERE h.id = %s", (himpunan_id,))
    himpunan = cursor.fetchone()
    kriteria = {'id': himpunan['kriteria_id'], 'nama_kriteria': himpunan['nama_kriteria']}
    cursor.close()
    conn.close()
    return render_template('admin/himpunan_edit.html', himpunan=himpunan, kriteria=kriteria)


@app.route('/admin/himpunan/hapus/<int:himpunan_id>', methods=['POST'])
@login_required
@admin_required
def admin_himpunan_hapus(himpunan_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT kriteria_id FROM himpunan_fuzzy WHERE id = %s", (himpunan_id,))
    kriteria_id = cursor.fetchone()['kriteria_id']
    
    try:
        cursor.execute("DELETE FROM himpunan_fuzzy WHERE id = %s", (himpunan_id,))
        conn.commit()
        flash('Himpunan fuzzy berhasil dihapus.', 'success')
        load_fuzzy_model()
    except mysql.connector.Error as err:
        flash(f'Gagal menghapus himpunan. Pastikan tidak ada aturan yang terkait. Error: {err}', 'danger')

    cursor.close()
    conn.close()
    return redirect(url_for('admin_himpunan_fuzzy', kriteria_id=kriteria_id))

# --- Manajemen Aturan ---
def get_kriteria_dan_himpunan_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kriteria")
    kriteria_list = cursor.fetchall()
    
    kriteria_data = {}
    for k in kriteria_list:
        cursor.execute("SELECT * FROM himpunan_fuzzy WHERE kriteria_id = %s", (k['id'],))
        himpunan_list = cursor.fetchall()
        kriteria_data[k['id']] = {
            'nama': k['nama_kriteria'],
            'tipe': k['tipe'],
            'himpunan': himpunan_list
        }
    cursor.close()
    conn.close()
    return kriteria_data

@app.route('/admin/aturan', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_aturan():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nama_aturan = request.form.get('nama_aturan')
        kondisi_ids = request.form.getlist('kondisi_himpunan_id')
        konsekuen_id = request.form.get('konsekuen_himpunan_id')
        
        # Filter out empty values
        kondisi_ids = [kid for kid in kondisi_ids if kid]

        if not kondisi_ids or not konsekuen_id:
            flash('Aturan tidak valid. Pastikan ada minimal 1 kondisi dan 1 konsekuen.', 'danger')
        else:
            try:
                # Insert a new rule
                cursor.execute("INSERT INTO aturan_fuzzy (nama_aturan) VALUES (%s)", (nama_aturan,))
                aturan_id = cursor.lastrowid
                
                # Insert conditions
                for himpunan_id in kondisi_ids:
                    cursor.execute("INSERT INTO kondisi_aturan (aturan_id, himpunan_id) VALUES (%s, %s)", (aturan_id, himpunan_id))
                
                # Insert consequent
                cursor.execute("INSERT INTO konsekuen_aturan (aturan_id, himpunan_id) VALUES (%s, %s)", (aturan_id, konsekuen_id))
                
                conn.commit()
                flash('Aturan baru berhasil disimpan!', 'success')
                load_fuzzy_model()
            except mysql.connector.Error as err:
                conn.rollback()
                flash(f'Gagal menyimpan aturan: {err}', 'danger')

        return redirect(url_for('admin_aturan'))

    # Untuk method GET
    cursor.execute("SELECT id, nama_aturan FROM aturan_fuzzy")
    aturan_list = cursor.fetchall()
    
    daftar_aturan_formatted = []
    for aturan in aturan_list:
        # Get conditions
        cursor.execute("""
            SELECT CONCAT(k.nama_kriteria, ' IS ', hf.nama_himpunan) as text
            FROM kondisi_aturan ka
            JOIN himpunan_fuzzy hf ON ka.himpunan_id = hf.id
            JOIN kriteria k ON hf.kriteria_id = k.id
            WHERE ka.aturan_id = %s
        """, (aturan['id'],))
        kondisi = ' <strong>AND</strong> '.join([row['text'] for row in cursor.fetchall()])
        
        # Get consequent
        cursor.execute("""
            SELECT CONCAT(k.nama_kriteria, ' IS ', hf.nama_himpunan) as text
            FROM konsekuen_aturan ca
            JOIN himpunan_fuzzy hf ON ca.himpunan_id = hf.id
            JOIN kriteria k ON hf.kriteria_id = k.id
            WHERE ca.aturan_id = %s
        """, (aturan['id'],))
        konsekuen = cursor.fetchone()
        
        daftar_aturan_formatted.append({
            'id': aturan['id'],
            'kondisi': f"<strong>IF</strong> {kondisi}" if kondisi else "NO CONDITION",
            'konsekuen': f"<strong>THEN</strong> {konsekuen['text']}" if konsekuen else "NO CONSEQUENT"
        })
        
    kriteria_data = get_kriteria_dan_himpunan_data()
    cursor.close()
    conn.close()
    return render_template('admin/aturan.html', daftar_aturan=daftar_aturan_formatted, kriteria_data=kriteria_data)


@app.route('/admin/aturan/edit/<int:aturan_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_aturan_edit(aturan_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nama_aturan = request.form.get('nama_aturan')
        kondisi_ids = [kid for kid in request.form.getlist('kondisi_himpunan_id') if kid]
        konsekuen_id = request.form.get('konsekuen_himpunan_id')
        
        try:
            # Update nama aturan
            cursor.execute("UPDATE aturan_fuzzy SET nama_aturan=%s WHERE id=%s", (nama_aturan, aturan_id))
            
            # Hapus kondisi lama dan masukkan yang baru
            cursor.execute("DELETE FROM kondisi_aturan WHERE aturan_id = %s", (aturan_id,))
            for himpunan_id in kondisi_ids:
                cursor.execute("INSERT INTO kondisi_aturan (aturan_id, himpunan_id) VALUES (%s, %s)", (aturan_id, himpunan_id))

            # Update konsekuen
            cursor.execute("DELETE FROM konsekuen_aturan WHERE aturan_id = %s", (aturan_id,))
            cursor.execute("INSERT INTO konsekuen_aturan (aturan_id, himpunan_id) VALUES (%s, %s)", (aturan_id, konsekuen_id))

            conn.commit()
            flash('Aturan berhasil diperbarui!', 'success')
            load_fuzzy_model()
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'Gagal memperbarui aturan: {err}', 'danger')
        
        return redirect(url_for('admin_aturan'))

    # Untuk method GET
    cursor.execute("SELECT * FROM aturan_fuzzy WHERE id=%s", (aturan_id,))
    aturan = cursor.fetchone()
    
    cursor.execute("SELECT * FROM kondisi_aturan WHERE aturan_id=%s", (aturan_id,))
    kondisi_list = cursor.fetchall()
    
    cursor.execute("SELECT * FROM konsekuen_aturan WHERE aturan_id=%s", (aturan_id,))
    konsekuen = cursor.fetchone()
    
    aturan_detail = {'kondisi': kondisi_list, 'konsekuen': konsekuen}
    kriteria_data = get_kriteria_dan_himpunan_data()
    
    cursor.close()
    conn.close()
    return render_template('admin/aturan_edit.html', aturan=aturan, aturan_detail=aturan_detail, kriteria_data=kriteria_data)

@app.route('/admin/aturan/hapus/<int:aturan_id>', methods=['POST'])
@login_required
@admin_required
def admin_aturan_hapus(aturan_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM aturan_fuzzy WHERE id = %s", (aturan_id,))
        conn.commit()
        flash('Aturan berhasil dihapus.', 'success')
        load_fuzzy_model()
    except mysql.connector.Error as err:
        flash(f'Gagal menghapus aturan: {err}', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('admin_aturan'))
# === RUTE-RUTE MAHASISWA (PERUBAHAN TOTAL) ===

@app.route('/mahasiswa/profil', methods=['GET', 'POST'])
@login_required
def profil_mahasiswa():
    # Pastikan hanya mahasiswa yang bisa mengakses
    if current_user.peran != 'mahasiswa':
        return redirect(url_for('index'))

    if request.method == 'POST':
        password_lama = request.form.get('password_lama')
        password_baru = request.form.get('password_baru')
        konfirmasi_password = request.form.get('konfirmasi_password')

        # Ambil data user dari DB untuk verifikasi password lama
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE id = %s", (current_user.id,))
        user_data = cursor.fetchone()
        
        # 1. Validasi Password Lama
        if not user_data or not check_password_hash(user_data['password'], password_lama):
            flash('Password lama yang Anda masukkan salah.', 'danger')
            return redirect(url_for('profil_mahasiswa'))

        # 2. Validasi Password Baru
        if not password_baru or not konfirmasi_password:
            flash('Password baru dan konfirmasi tidak boleh kosong.', 'warning')
            return redirect(url_for('profil_mahasiswa'))
        
        if password_baru != konfirmasi_password:
            flash('Password baru dan konfirmasi password tidak cocok.', 'warning')
            return redirect(url_for('profil_mahasiswa'))
            
        # 3. Jika semua validasi lolos, update password
        password_hash_baru = generate_password_hash(password_baru)
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (password_hash_baru, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Password Anda berhasil diperbarui!', 'success')
        return redirect(url_for('profil_mahasiswa'))

    # Untuk method GET, cukup tampilkan halaman
    return render_template('mahasiswa/profil.html')

@app.route('/mahasiswa/dashboard')
@login_required
def dashboard_mahasiswa():
    if current_user.peran != 'mahasiswa': return redirect(url_for('login'))
    return render_template('mahasiswa/dashboard_welcome.html')

@app.route('/mahasiswa/pengecekan')
@login_required
def halaman_pengecekan():
    if current_user.peran != 'mahasiswa': return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT kode_kriteria, nama_kriteria FROM kriteria WHERE tipe = 'input' ORDER BY id")
    kriteria_rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    kriteria_input = [{'kode_kriteria': k['kode_kriteria'].lower(), 'nama_kriteria': k['nama_kriteria']} for k in kriteria_rows]
    chart_data = generate_chart_data()

    return render_template('mahasiswa/pengecekan.html', kriteria_input=kriteria_input, chart_data=chart_data)


# Di dalam app.py, ganti seluruh fungsi cek_kelayakan
@app.route('/mahasiswa/cek_kelayakan', methods=['POST'])
@login_required
def cek_kelayakan():
    if current_user.peran != 'mahasiswa':
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        # Panggil load_fuzzy_model untuk memastikan model terbaru yang digunakan
        load_fuzzy_model()
        inputs = {key: float(value) for key, value in request.form.items()}
        
        # LANGKAH 1: Jalankan Mesin Fuzzy untuk mendapatkan skor & fakta linguistik
        skor_fuzzy, interpretasi_fuzzy, aturan_aktif_fuzzy, fakta_linguistik = run_inference_engine(inputs)

        # LANGKAH 2: Inisialisasi Sistem Pakar
        kb = KnowledgeBase()
        engine = InferenceEngine()
        
        # LANGKAH 3: Masukkan fakta dari hasil fuzzy ke basis pengetahuan pakar
        kb.facts = fakta_linguistik
            
        # LANGKAH 4: Jalankan Mesin Inferensi Pakar
        hasil_pakar = engine.infer(kb)

        # LANGKAH 5: Kembalikan semua hasil dalam format JSON
        return jsonify({
            'status': 'sukses',
            'hasil_fuzzy': {
                'skor': skor_fuzzy,
                'interpretasi': interpretasi_fuzzy,
                'aturan_aktif': aturan_aktif_fuzzy[:3] # Ambil 3 teratas
            },
            'hasil_pakar': hasil_pakar
        })

    except Exception as e:
        print(f"Error pada saat cek kelayakan: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    # FUNGSI HELPER BARU UNTUK MENGUBAH INPUT ANGKA MENJADI KATEGORI
def kategorikan_input(inputs):
    """Mengubah input numerik menjadi fakta linguistik/kualitatif."""
    fakta = {}

    # 1. Kategorisasi Penghasilan (dalam juta)
    penghasilan = inputs.get('penghasilan', 0)
    if penghasilan <= 2.5:
        fakta['penghasilan'] = 'Rendah'
    elif penghasilan <= 5.5:
        fakta['penghasilan'] = 'Sedang'
    else:
        fakta['penghasilan'] = 'Tinggi'

    # 2. Kategorisasi Nilai Rata-rata Rapor
    nilai = inputs.get('nilai', 0)
    if nilai >= 85:
        fakta['nilai'] = 'Tinggi'
    elif nilai >= 70:
        fakta['nilai'] = 'Sedang'
    else:
        fakta['nilai'] = 'Rendah'

    # 3. Kategorisasi Jumlah Tanggungan
    tanggungan = inputs.get('tanggungan', 0)
    if tanggungan >= 5:
        fakta['tanggungan'] = 'Banyak'
    elif tanggungan >= 3:
        fakta['tanggungan'] = 'Sedang'
    else:
        fakta['tanggungan'] = 'Sedikit'

    # 4. Kategorisasi Poin Prestasi
    prestasi = inputs.get('prestasi', 0)
    if prestasi >= 70:
        fakta['prestasi'] = 'Tinggi'
    elif prestasi >= 30:
        fakta['prestasi'] = 'Sedang'
    else:
        fakta['prestasi'] = 'Rendah'
        
    return fakta

@app.route('/admin/pengguna')
@login_required
@admin_required
def admin_daftar_pengguna():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # UBAH QUERY INI: Tambahkan "WHERE peran = 'mahasiswa'"
    cursor.execute("SELECT id, nama_lengkap, username, peran FROM users WHERE peran = 'mahasiswa' ORDER BY id")
    daftar_pengguna = cursor.fetchall()
    cursor.close()
    conn.close()
    # Pastikan nama file template sesuai
    return render_template('admin/daftar_pengguna.html', daftar_pengguna=daftar_pengguna)

# Blok eksekusi utama
if __name__ == '__main__':
    with app.app_context():
        load_fuzzy_model()
    app.run(debug=True)