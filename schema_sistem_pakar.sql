-- Skema untuk Database Sistem Pakar Beasiswa
-- Didesain untuk kejelasan dan kemudahan pengelolaan.

-- Selalu mulai dengan menghapus tabel lama jika ada (dengan urutan yang benar)
DROP TABLE IF EXISTS `kondisi_aturan`;
DROP TABLE IF EXISTS `konsekuen_aturan`;
DROP TABLE IF EXISTS `aturan_fuzzy`;
DROP TABLE IF EXISTS `himpunan_fuzzy`;
DROP TABLE IF EXISTS `kriteria`;
DROP TABLE IF EXISTS `users`;

-- Tabel 1: Untuk manajemen pengguna (admin dan mahasiswa)
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nama_lengkap` VARCHAR(255) NOT NULL,
  `username` VARCHAR(100) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `peran` ENUM('admin', 'mahasiswa') NOT NULL DEFAULT 'mahasiswa',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel 2: Untuk kriteria input (Penghasilan, Nilai) dan output (Kelayakan)
CREATE TABLE `kriteria` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `kode_kriteria` VARCHAR(50) NOT NULL UNIQUE,
  `nama_kriteria` VARCHAR(100) NOT NULL,
  `tipe` ENUM('input', 'output') NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel 3: Untuk himpunan fuzzy (Rendah, Sedang, Tinggi) yang terhubung ke kriteria
CREATE TABLE `himpunan_fuzzy` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `kriteria_id` INT NOT NULL,
  `nama_himpunan` VARCHAR(50) NOT NULL,
  `nilai1` DOUBLE NOT NULL,
  `nilai2` DOUBLE NOT NULL,
  `nilai3` DOUBLE NOT NULL,
  `nilai4` DOUBLE NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`kriteria_id`) REFERENCES `kriteria`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel 4: Kerangka utama untuk aturan fuzzy
CREATE TABLE `aturan_fuzzy` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nama_aturan` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel 5: Untuk bagian 'IF' dari aturan (bisa memiliki banyak kondisi)
CREATE TABLE `kondisi_aturan` (
  `aturan_id` INT NOT NULL,
  `himpunan_id` INT NOT NULL,
  PRIMARY KEY (`aturan_id`, `himpunan_id`),
  FOREIGN KEY (`aturan_id`) REFERENCES `aturan_fuzzy`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`himpunan_id`) REFERENCES `himpunan_fuzzy`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel 6: Untuk bagian 'THEN' dari aturan (hanya satu konsekuen per aturan)
CREATE TABLE `konsekuen_aturan` (
  `aturan_id` INT NOT NULL,
  `himpunan_id` INT NOT NULL,
  PRIMARY KEY (`aturan_id`),
  FOREIGN KEY (`aturan_id`) REFERENCES `aturan_fuzzy`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`himpunan_id`) REFERENCES `himpunan_fuzzy`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;