# Tugas 6 - Mini Proyek Tree-sitter

CLI `cek.py` memeriksa file Python dalam sebuah folder menggunakan Tree-sitter.

## Fitur

1. Menemukan komentar yang mengandung `TODO` atau `FIXME`, beserta nama file dan nomor baris.
2. Menemukan fungsi yang panjangnya lebih dari 30 baris.
3. Menemukan file yang pohon sintaksnya memiliki error, lalu menampilkan node `ERROR` atau `MISSING` pertama yang ditemukan.

## Instalasi

Pastikan Python 3.10 atau lebih baru tersedia. Pasang dependensi:

```bash
python -m pip install tree-sitter tree-sitter-python
```

## Menjalankan

Dari folder proyek, jalankan:

```bash
python cek/cek.py <folder_yang_diperiksa>
```

Contoh:

```bash
python cek/cek.py cek/uji
```

Skrip memeriksa file berekstensi `.py` secara rekursif. Folder `.git`, `.venv`, `venv`, `__pycache__`, dan `node_modules` dilewati.

## Cara kerja singkat

- Query `Q_TODO` memakai capture `@c` dan predikat `#match?` untuk mencari komentar yang memuat `TODO` atau `FIXME`.
- Query `Q_FUNCTION` menangkap nama fungsi (`@nama`) dan node fungsi (`@fungsi`). Jumlah baris dihitung dari `start_point` dan `end_point`.
- `root_node.has_error` digunakan untuk mengetahui apakah pohon memiliki error. Jika ada, fungsi `cari_error()` menelusuri node untuk menemukan `ERROR` atau `MISSING` pertama.

## Pengujian

Buat beberapa file Python di dalam satu folder uji:
- satu file dengan komentar `# TODO`,
- satu file dengan fungsi yang panjangnya lebih dari 30 baris,
- satu file dengan sintaks Python yang sengaja dirusak.

Jalankan CLI pada folder tersebut, lalu cocokkan temuan dengan isi file secara manual.

**## Hasil Pengujian**

Pengujian dilakukan menggunakan folder `cek/uji` yang berisi tiga file Python dengan kondisi berbeda. Program berhasil mendeteksi komentar TODO, fungsi yang memiliki panjang lebih dari 30 baris, dan kesalahan sintaks.

Pengujian juga dilakukan pada folder utama proyek menggunakan perintah:

```bash
python cek/cek.py .
```

Program berhasil memeriksa 15 file Python dan menampilkan temuan sesuai kondisi file yang diperiksa.