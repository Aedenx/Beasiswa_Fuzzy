# fuzzy_engine.py
import mysql.connector
import numpy as np

FUZZY_MODEL = { "kriteria_input": {}, "kriteria_output": {}, "aturan": [] }

# Di dalam fuzzy_engine.py
def get_db_connection():
    try:
        # UBAH BARIS INI JUGA
        return mysql.connector.connect(host="localhost", user="root", password="", database="db_sistem_pakar")
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def _hitung_derajat_keanggotaan(x, params):
    a, b, c, d = params['nilai1'], params['nilai2'], params['nilai3'], params['nilai4']
    if a > b: b = a
    if b > c: c = b
    if c > d: d = c
    if x <= a or x >= d: return 0.0
    if a < x < b: return (x - a) / (b - a) if b != a else 1.0
    if b <= x <= c: return 1.0
    if c < x < d: return (d - x) / (d - c) if d != c else 1.0
    return 0.0

def fuzzify(inputs):
    fuzzified_values = {}
    for kode_kriteria, nilai_input in inputs.items():
        fuzzified_values[kode_kriteria.upper()] = {}
        himpunan_list = FUZZY_MODEL['kriteria_input'].get(kode_kriteria.upper())
        if himpunan_list:
            for himpunan in himpunan_list:
                nama_himpunan = himpunan['nama_himpunan']
                fuzzified_values[kode_kriteria.upper()][nama_himpunan] = _hitung_derajat_keanggotaan(float(nilai_input), himpunan)
    return fuzzified_values

def interpret_inputs(inputs):
    """
    FUNGSI BARU: Menerjemahkan input numerik menjadi fakta linguistik.
    Ini adalah jembatan antara Fuzzy Engine dan Expert System Engine.
    """
    fuzzified = fuzzify(inputs)
    linguistic_facts = {}
    for kode_kriteria, himpunan_derajat in fuzzified.items():
        if not himpunan_derajat: continue
        # Cari nama himpunan dengan derajat keanggotaan tertinggi
        best_term = max(himpunan_derajat, key=himpunan_derajat.get)
        linguistic_facts[kode_kriteria.lower()] = best_term
    return linguistic_facts

def interpret_skor(skor):
    output_kriteria_key = list(FUZZY_MODEL['kriteria_output'].keys())[0]
    output_himpunan = FUZZY_MODEL['kriteria_output'][output_kriteria_key]
    max_derajat, interpretasi_terbaik = 0, "Tidak Terdefinisi"
    for himpunan in output_himpunan:
        derajat = _hitung_derajat_keanggotaan(skor, himpunan)
        if derajat > max_derajat:
            max_derajat, interpretasi_terbaik = derajat, himpunan['nama_himpunan']
    return interpretasi_terbaik

def run_inference_engine(inputs):
    """
    Orkestrator utama Fuzzy. Sekarang mengembalikan 4 nilai, termasuk fakta linguistik.
    """
    if not FUZZY_MODEL['aturan']: load_fuzzy_model()
    
    fuzzified_inputs = fuzzify(inputs)
    linguistic_facts = interpret_inputs(inputs)

    rule_strengths = []
    for aturan in FUZZY_MODEL['aturan']:
        kondisi_values = [fuzzified_inputs.get(k['kode_kriteria'], {}).get(k['nama_himpunan'], 0.0) for k in aturan['kondisi']]
        alpha = min(kondisi_values) if kondisi_values else 0.0
        if alpha > 0:
            rule_strengths.append({'alpha': alpha, 'konsekuen': aturan['konsekuen']})

    if not rule_strengths:
        return 0.0, "Tidak Terdefinisi", [], linguistic_facts

    # Proses Defuzzifikasi (Centroid of Area)
    output_kriteria_key = list(FUZZY_MODEL['kriteria_output'].keys())[0]
    output_himpunan_list = FUZZY_MODEL['kriteria_output'][output_kriteria_key]
    all_values = [h[f"nilai{i+1}"] for h in output_himpunan_list for i in range(4)]
    x_min, x_max = min(all_values), max(all_values)
    sample_points = np.linspace(x_min, x_max, 100)
    
    numerator, denominator = 0.0, 0.0
    for x in sample_points:
        aggregated_membership = max([min(s['alpha'], _hitung_derajat_keanggotaan(x, s['konsekuen'])) for s in rule_strengths] or [0])
        numerator += x * aggregated_membership
        denominator += aggregated_membership

    final_score = numerator / denominator if denominator != 0 else 0.0
    final_interpretation = interpret_skor(final_score)
    activated_rules_details = [{'nama': s['konsekuen']['nama_aturan'], 'alpha': round(s['alpha'], 2)} for s in sorted(rule_strengths, key=lambda i: i['alpha'], reverse=True)]

    return round(final_score, 2), final_interpretation, activated_rules_details, linguistic_facts

# Fungsi load_fuzzy_model dan generate_chart_data tetap sama persis seperti yang Anda miliki.
# Pastikan fungsi-fungsi tersebut ada di bawah kode ini.

def load_fuzzy_model():
    """Mengambil semua data fuzzy (kriteria, himpunan, aturan) dari DB."""
    global FUZZY_MODEL
    FUZZY_MODEL = {"kriteria_input": {}, "kriteria_output": {}, "aturan": []}
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kriteria")
    kriteria_list = cursor.fetchall()
    for k in kriteria_list:
        cursor.execute("SELECT * FROM himpunan_fuzzy WHERE kriteria_id = %s ORDER BY nilai1", (k['id'],))
        himpunan_list = cursor.fetchall()
        if k['tipe'] == 'input': FUZZY_MODEL['kriteria_input'][k['kode_kriteria']] = himpunan_list
        else: FUZZY_MODEL['kriteria_output'][k['kode_kriteria']] = himpunan_list
    cursor.execute("SELECT id, nama_aturan FROM aturan_fuzzy")
    aturan_list = cursor.fetchall()
    for a in aturan_list:
        cursor.execute("SELECT hf.*, k.kode_kriteria FROM kondisi_aturan ka JOIN himpunan_fuzzy hf ON ka.himpunan_id = hf.id JOIN kriteria k ON hf.kriteria_id = k.id WHERE ka.aturan_id = %s", (a['id'],))
        kondisi = cursor.fetchall()
        cursor.execute("SELECT hf.* FROM konsekuen_aturan ca JOIN himpunan_fuzzy hf ON ca.himpunan_id = hf.id WHERE ca.aturan_id = %s", (a['id'],))
        konsekuen = cursor.fetchone()
        if kondisi and konsekuen:
            if konsekuen and a.get('nama_aturan'): konsekuen['nama_aturan'] = a['nama_aturan']
            FUZZY_MODEL['aturan'].append({'kondisi': kondisi, 'konsekuen': konsekuen})
    cursor.close()
    conn.close()
    print("Model Fuzzy berhasil dimuat ulang dari database.")

def generate_chart_data():
    if not FUZZY_MODEL['kriteria_input']: load_fuzzy_model()
    chart_data = {}
    for kode, daftar_himpunan in FUZZY_MODEL['kriteria_input'].items():
        all_values = [h[f"nilai{i+1}"] for h in daftar_himpunan for i in range(4)]
        if not all_values: continue
        x_min, x_max = min(all_values), max(all_values)
        padding = (x_max - x_min) * 0.1 if (x_max - x_min) > 0 else 1
        x_range = np.linspace(x_min - padding, x_max + padding, 100)
        datasets = []
        for himpunan in daftar_himpunan:
            y_values = [_hitung_derajat_keanggotaan(x, himpunan) for x in x_range]
            datasets.append({"label": himpunan['nama_himpunan'], "data": y_values})
        chart_data[kode.lower()] = {"labels": [round(x, 2) for x in x_range], "datasets": datasets}
    return chart_data