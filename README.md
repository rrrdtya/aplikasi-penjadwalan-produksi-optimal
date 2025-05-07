# Aplikasi Penjadwalan Produksi Optimal dengan Integer Programming

Aplikasi web untuk mengoptimalkan penjadwalan produksi dengan metode Integer Linear Programming (ILP) menggunakan PuLP solver.

## Deskripsi

Aplikasi ini membantu mengoptimalkan penjadwalan produksi berdasarkan keterbatasan mesin dan waktu produksi. Dibuat untuk memenuhi tugas Mata Kuliah - Kelompok 6.

## Fitur Utama

1. Input waktu mesin, produk, dan batas waktu
2. Menggunakan solver ILP (PuLP di Python)
3. Output berupa jadwal produksi optimal
4. Visualisasi alokasi mesin ke produk

## Teknologi yang Digunakan

- Python 3.8+
- Flask
- PuLP (Solver Linear Programming)
- Matplotlib (Visualisasi)
- Bootstrap 5
- HTML/CSS/JavaScript

## Cara Menjalankan Aplikasi

1. Pastikan Python 3.8+ sudah terinstall
2. Clone repository ini
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Jalankan aplikasi:
   ```
   python run.py
   ```
5. Buka browser dan akses `http://localhost:5000`

## Contoh Kasus

Optimasi penjadwalan produksi berdasarkan keterbatasan mesin dan waktu:
- 5 produk yang harus diproduksi: P1, P2, P3, P4, P5
- 3 mesin yang tersedia: M1, M2, M3
- Waktu produksi per unit produk:
  - P1: 2 jam pada M1
  - P2: 3 jam pada M2
  - P3: 4 jam pada M1
  - P4: 1 jam pada M3
  - P5: 2 jam pada M2
- Keterbatasan waktu produksi: 10 jam per hari

## Metodologi

Metode Integer Linear Programming (ILP) adalah teknik optimasi untuk mencapai hasil terbaik dalam model matematika dengan batasan yang dinyatakan sebagai hubungan linear dan variabel keputusan yang harus berupa bilangan bulat.

### Langkah-langkah Penyelesaian:

1. Mendefinisikan variabel keputusan
2. Menentukan fungsi tujuan
3. Menentukan batasan-batasan
4. Menggunakan solver ILP untuk mendapatkan solusi optimal

## Screenshot

(Screenshot akan tersedia setelah aplikasi berjalan)

## Pengembang

Kelompok 6 - Aplikasi Penjadwalan Produksi Optimal dengan Integer Programming 