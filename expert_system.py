# expert_system.py (Versi Final dengan Bahasa Profesional & Memotivasi)

class KnowledgeBase:
    """Menyimpan fakta dan aturan-aturan kualitatif dari seorang pakar."""
    def __init__(self):
        self.facts = {}
        self.rules = []
        self._load_expert_rules()

    def _add_rule(self, condition, action, explanation):
        """Metode internal untuk menambahkan aturan ke basis pengetahuan."""
        self.rules.append({
            'condition': condition,
            'action': action,
            'reason': explanation
        })

    def _load_expert_rules(self):
        """
        Pusat Basis Pengetahuan Pakar dengan Prinsip P.A.S.
        (Pujian, Analisis, Saran)
        """
        # --- KELOMPOK ATURAN UNTUK HASIL SANGAT POSITIF ---
        self._add_rule(
            condition=lambda f: f.get('penghasilan') == 'Rendah' and f.get('nilai') == 'Tinggi' and f.get('prestasi') == 'Tinggi',
            action="Sangat Direkomendasikan (Profil Ideal)",
            explanation=lambda f: (
                f"Selamat, profil Anda sangat menonjol! (Pujian). "
                f"Kombinasi prestasi akademik ('{f.get('nilai')}') dan non-akademik ('{f.get('prestasi')}') yang luar biasa, didukung oleh latar belakang ekonomi ('{f.get('penghasilan')}') yang sesuai, menjadikan Anda kandidat prioritas utama kami. (Analisis). "
                f"Saran kami, segera persiapkan kelengkapan dokumen Anda dan pantau terus jadwal seleksi berikutnya. (Saran)."
            )
        )
        self._add_rule(
            condition=lambda f: f.get('nilai') == 'Tinggi' and f.get('prestasi') == 'Tinggi',
            action="Direkomendasikan (Jalur Prestasi)",
            explanation=lambda f: (
                f"Prestasi Anda di bidang akademik ('{f.get('nilai')}') dan non-akademik ('{f.get('prestasi')}') sangat mengesankan. (Pujian). "
                f"Anda sangat direkomendasikan melalui jalur prestasi karena keunggulan ini. (Analisis). "
                f"Saran kami, pastikan semua sertifikat prestasi terbaik Anda dilampirkan untuk memaksimalkan peluang. (Saran)."
            )
        )
        self._add_rule(
            condition=lambda f: f.get('penghasilan') == 'Rendah' and f.get('nilai') == 'Tinggi',
            action="Direkomendasikan (Prioritas Akademik & Ekonomi)",
            explanation=lambda f: (
                f"Kerja keras Anda membuahkan hasil yang sangat baik! (Pujian). "
                f"Nilai akademik Anda yang '{f.get('nilai')}' dengan latar belakang ekonomi ('{f.get('penghasilan')}') menjadikan Anda kandidat kuat yang sesuai dengan misi beasiswa ini. (Analisis). "
                f"Saran kami, fokus pada penulisan esai atau motivation letter yang menonjolkan kegigihan Anda. (Saran)."
            )
        )

        # --- KELOMPOK ATURAN UNTUK HASIL "DIpertimbangkan" ---
        self._add_rule(
            condition=lambda f: f.get('prestasi') == 'Tinggi' or f.get('nilai') == 'Tinggi',
            action="Masuk Daftar Pertimbangan",
            explanation=lambda f: (
                f"Anda memiliki setidaknya satu keunggulan yang menonjol, baik itu di bidang akademik ('{f.get('nilai')}') ataupun non-akademik ('{f.get('prestasi')}'). (Pengakuan). "
                f"Profil Anda telah kami masukkan ke dalam daftar kandidat yang akan dievaluasi lebih lanjut bersama pendaftar lainnya. (Analisis). "
                f"Saran kami, tidak ada tindakan yang perlu dilakukan saat ini selain menunggu pengumuman resmi. Semoga berhasil! (Saran)."
            )
        )

        # --- KELOMPOK ATURAN UNTUK HASIL NEGATIF (DENGAN SOLUSI) ---
        self._add_rule(
            condition=lambda f: f.get('nilai') == 'Rendah' and f.get('prestasi') == 'Rendah',
            action="Belum Memenuhi Kualifikasi",
            explanation=lambda f: (
                f"Terima kasih atas partisipasi dan semangat Anda untuk mendaftar. (Pengakuan). "
                f"Berdasarkan evaluasi, kualifikasi Anda pada kriteria Nilai Akademik ('{f.get('nilai')}') dan Prestasi Non-Akademik ('{f.get('prestasi')}') saat ini belum mencapai ambang batas minimum yang dibutuhkan. (Analisis). "
                f"Saran kami, mari fokus untuk meningkatkan IPK di semester depan dan coba ikuti 1-2 kegiatan organisasi/kompetisi untuk membangun portofolio. Kami sangat menantikan Anda mendaftar kembali di periode selanjutnya dengan profil yang lebih kuat! (Saran & Motivasi)."
            )
        )
        self._add_rule(
            condition=lambda f: f.get('penghasilan') == 'Tinggi',
            action="Tidak Menjadi Prioritas",
            explanation=lambda f: (
                f"Kami menghargai pencapaian Anda sejauh ini. (Pengakuan). "
                f"Program beasiswa ini secara spesifik ditujukan untuk membantu mahasiswa dengan keterbatasan ekonomi. Berdasarkan data, kondisi ekonomi Anda yang tergolong '{f.get('penghasilan')}' membuat prioritas diberikan kepada yang lain. (Analisis). "
                f"Saran kami, jangan berkecil hati. Ada banyak program beasiswa berbasis prestasi murni (merit-based) yang tidak mempertimbangkan faktor ekonomi, yang mungkin sangat cocok untuk Anda. (Saran & Solusi)."
            )
        )
        
        # --- ATURAN DEFAULT (PALING AKHIR) ---
        self._add_rule(
            condition=lambda f: True,
            action="Memerlukan Tinjauan Manual",
            explanation="Terima kasih telah melengkapi data. Kombinasi kriteria Anda unik dan memerlukan tinjauan lebih lanjut secara manual oleh tim kami. Mohon tunggu informasi berikutnya."
        )


class InferenceEngine:
    """Mengevaluasi fakta terhadap aturan untuk menarik kesimpulan."""
    def _evaluate_condition(self, condition_func, facts):
        try:
            return condition_func(facts)
        except Exception:
            return False

    def infer(self, knowledge_base):
        """Menjalankan proses inferensi."""
        for rule in knowledge_base.rules:
            if self._evaluate_condition(rule['condition'], knowledge_base.facts):
                penjelasan_final = ""
                if callable(rule['reason']):
                    penjelasan_final = rule['reason'](knowledge_base.facts)
                else:
                    penjelasan_final = rule['reason']

                return {
                    'rekomendasi': rule['action'],
                    'penjelasan': penjelasan_final
                }
        return None