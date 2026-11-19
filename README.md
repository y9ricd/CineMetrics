# CineMetrics: Sistem Cerdas Penaksir Kualitas & Skor Film Berbasis Web Django

> **Tugas Akhir Mata Kuliah Sistem Cerdas**  
> **Pengembangan Modul 14 (Deployment Model Machine Learning) & Praktikum P07**  
> Program Studi D3 / D4 Teknologi Informasi — Politeknik Negeri Madiun

---

## 1. Deskripsi Aplikasi & Tujuan Pengguna

**CineMetrics** adalah aplikasi berbasis web yang mengintegrasikan model _Machine Learning_ ke dalam framework **Django** untuk memprediksi kualitas dan mengestimasi skor film layar lebar. Aplikasi ini dikembangkan sebagai pemenuhan **Tugas Akhir Modul 14**, mengadopsi model dan dataset eksplorasi film dari penugasan **P07**.

### Tujuan Pengguna & Nilai Bisnis:

1. **Bagi Produser / Rumah Produksi:** Memberikan estimasi awal apakah sebuah rancangan film (berdasarkan durasi, proyeksi ulasan audiens, dan anggaran) berpotensi masuk ke kategori film _Sangat Bagus_, _Bagus_, atau berisiko _Kurang_.
2. **Bagi Kritikus & Audiens:** Memberikan proyeksi skor IMDb berbasis data historis 5.400+ film dunia.
3. **Penerapan Prinsip Modul 14 (_Deployment Best Practices_):**
   - Serialisasi model menggunakan `joblib` (`joblib.dump` dan `joblib.load`).
   - Menerapkan _Golden Rule Deployment_: matriks fitur input pengguna disusun persis sama (urutan kolom, nama fitur, tipe data) seperti saat model dilatih.
   - Antarmuka web responsif dengan validasi form yang mencegah _invalid inputs_ (durasi $\le 0$ atau anggaran negatif).

---

## 2. Arsitektur Sistem Cerdas

```
[ Dataset: movies_clean.csv ]
              │
              ▼
    [ ml_model/train_and_export.py ]
              │
      ┌───────┴────────────────────────┐
      ▼                                ▼
[ model_quality.joblib ]      [ model_score.joblib ]
(DecisionTreeClassifier)      (LinearRegression)
      │                                │
      └───────────────┬────────────────┘
                      ▼
            [ Django Framework ]
       ┌──────────────────────────────┐
       │  predictor/views.py          │
       │  - Model Caching (Memory)    │
       │  - Input Dataframe Assembly  │
       │  - .predict() & Probabilities│
       └──────────────┬───────────────┘
                      ▼
      [ User Interface: Bootstrap 5 ]
       - Form Input Parameter Film
       - Status Badge Kualitas & Skor IMDb
       - Visualisasi Feature Importance
```

### Rincian Model yang Digunakan:

1. **Klasifikasi Kualitas Film (`DecisionTreeClassifier`, max_depth=3):**
   - **Fitur Input:** `runtime` (durasi menit), `votes` (jumlah ulasan), `budget` (anggaran USD), `year` (tahun rilis).
   - **Target Output:** Kategori diskrit:
     - `Kurang`: Skor < 6.0
     - `Bagus`: Skor 6.0 s.d. < 7.0
     - `Sangat Bagus`: Skor $\ge$ 7.0
   - **Faktor Penentu Terbesar (_Feature Importance_):** Resonansi Votes (~68.3%), Durasi Tayang (~19.0%), Anggaran (~12.7%), dan Tahun Rilis (0.0%).
2. **Estimasi Skor IMDb (`LinearRegression`):**
   - **Fitur Input:** `runtime`, `votes`.
   - **Target Output:** Skor kontinu IMDb (skala 1.0 – 10.0).

---

## 3. Struktur Direktori Proyek

```text
Tugas Akhir/
├── manage.py                     # Skrip manajemen utama Django
├── requirements.txt              # Daftar pustaka & dependensi
├── README.md                     # Dokumentasi proyek (Modul 14)
├── TUGAS_INDIVIDU_REFLEKSI.md    # Jawaban refleksi AI Sub-CPMK 0812 & 0832
│
├── ml_model/                     # Pipeline Machine Learning
│   ├── movies_clean.csv          # Dataset film yang telah dibersihkan
│   ├── train_and_export.py       # Skrip pelatihan & serialisasi model
│   ├── model_quality.joblib      # Biner model klasifikasi (Decision Tree)
│   ├── model_score.joblib        # Biner model regresi (Linear Regression)
│   └── model_meta.json           # Metadata statistik & bobot fitur
│
├── movie_system/                 # Konfigurasi Inti Django
│   ├── settings.py               # Pengaturan aplikasi & static files
│   ├── urls.py                   # Routing utama
│   └── wsgi.py
│
└── predictor/                    # Django Application
    ├── forms.py                  # Validasi form input pengguna
    ├── views.py                  # Logika inferensi model ML
    ├── urls.py                   # Routing aplikasi predictor
    ├── tests.py                  # Pengujian otomatis (Unit Testing)
    └── templates/
        └── predictor/
            ├── base.html         # Template layout induk Bootstrap 5
            └── index.html        # Antarmuka form input & kartu hasil
```

---

## 4. Petunjuk Instalasi & Cara Menjalankan

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di komputer lokal:

### Prasyarat:

- Python 3.10, 3.11, atau 3.12 terinstal di komputer.
- Git (opsional).

### Langkah 1: Buka Terminal pada Folder Proyek

```bash
cd "d:/SEMESTER 3/Tugas Akhir"
```

### Langkah 2: (Opsional) Buat & Aktifkan Virtual Environment

```bash
# Membuat virtual environment
python -m venv venv

# Mengaktifkan di Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Atau jika di Command Prompt (cmd):
.\venv\Scripts\activate.bat
```

### Langkah 3: Pasang Dependensi Pustaka

```bash
pip install -r requirements.txt
```

### Langkah 4: Migrasi Database SQLite

Inisialisasi tabel database (termasuk tabel `PredictionHistory`):

```bash
python manage.py migrate
```

### Langkah 5: (Opsional) Latih Ulang Model

Jika ingin melatih ulang model dari file `movies_clean.csv`:

```bash
python ml_model/train_and_export.py
```

### Langkah 6: Jalankan Unit Test

Pastikan seluruh komponen berfungsi tanpa error:

```bash
python manage.py test predictor
```

### Langkah 7: Jalankan Aplikasi Web

Tersedia dua mode antarmuka:

#### Mode 1: Aplikasi Streamlit (Standar Resmi Deliverable Modul 14)

Sesuai instruksi Modul 14 (_"Streamlit membungkus model menjadi aplikasi web tanpa HTML/CSS, deliverable file app.py"_):

- **Cara 1 (Double-Click):** Klik dua kali file **`run_streamlit.bat`**.
- **Cara 2 (PowerShell):**
  ```powershell
  .\run_streamlit.ps1
  # atau
  .\venv\Scripts\python.exe -m streamlit run app.py
  ```
  Buka browser di: **`http://localhost:8501/`**

---

#### Mode 2: Aplikasi Web Django (Versi Enterprise / Fullstack)

- **Cara 1 (Double-Click):** Klik dua kali file **`run.bat`**.
- **Cara 2 (PowerShell):**
  ```powershell
  .\run.ps1
  # atau
  .\venv\Scripts\python.exe manage.py runserver
  ```
  Buka browser di: **`http://127.0.0.1:8000/`**

---

## 5. Sumber Dataset & Keterangan Lisensi

- **Dataset:** _Movie Industry Dataset_ (Kaggle / IMDb public data).
- **Jumlah Baris:** 5.421 film (setelah pembersihan nilai kosong dan filter `budget > 0`).
- **Lisensi Data:** CC0: Public Domain (bebas digunakan untuk keperluan riset, akademik, dan edukasi).
- **Atribusi:** Data dikurasi dan disesuaikan dari materi praktikum _Sistem Cerdas (P07)_.

---

## 6. Identitas Pengembang & Pembagian Peran

Proyek ini dikembangkan sebagai pemenuhan Tugas Akhir Mata Kuliah Sistem Cerdas oleh:

| NIM | Nama Pengembang | Program Studi | Peran & Kontribusi Utama |
| :--- | :--- | :--- | :--- |
| **253307025** | **Mohammad Saputra Abdul Farid** | D3 Teknologi Informasi | **Fullstack ML Developer & System Architect:** Preprocessing dataset film P07, implementasi training Decision Tree & Linear Regression, ekspor serialisasi `.joblib`, perancangan arsitektur backend Django (caching, form validation, deduplikasi, logging), integrasi CineBot AI dengan fallback rule-based, perancangan antarmuka visualisasi interaktif Bootstrap 5, serta pengujian otomatis (Unit Testing). |

---

## 7. Rubrik Penilaian Modul 14 (Checklist Kesesuaian)

- [x] **Fungsi Aplikasi (Skor 8):** Form input lengkap (durasi, vote, budget, tahun), inferensi model berjalan mulus, validasi edge case aktif, dan visualisasi distribusi probabilitas serta _feature importance_.
- [x] **Pemahaman Kode & Demo (Skor 6):** Arsitektur kode bersih, pemisahan folder `ml_model` dan `predictor`, penggunaan `joblib.load` dengan efisiensi memori.
- [x] **Kerja Sama & Pembagian Peran (Skor 3):** Identitas pengembang terinci dan tugas terbagi proporsional mencakup seluruh siklus machine learning deployment.
- [x] **Dokumentasi & Kerapian (Skor 3):** Petunjuk instalasi dapat direproduksi secara mandiri dari terminal dengan `requirements.txt`.
