# Movie Intelligence (Django + ML Deployment) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Membangun aplikasi web cerdas berbasis Django untuk deployment model Machine Learning prediksi kualitas dan skor film (dataset movies P07) sesuai standar penugasan Modul 14 Sistem Cerdas.

**Architecture:** Model dilatih dan diserialisasi menggunakan `joblib` di modul `ml_model/`. Framework Django (MVT) menangani request input pengguna melalui web form, melakukan validasi batasan nilai, mengonstruksi DataFrame input yang identik dengan feature matrix $X$, menjalankan inferensi model, dan merender tampilan antarmuka responsif dengan Bootstrap 5.

**Tech Stack:** Python 3, Django, Scikit-learn, Pandas, NumPy, Joblib, Bootstrap 5.

**Spec:** Pedoman Modul 14 (Deployment dengan Streamlit & Mini Proyek Kelompok) dan Notebook P07 (Praktikum Sistem Cerdas).

## Global Constraints

- Struktur fitur input $X$ saat inferensi harus identik dalam nama kolom, tipe data, dan urutan dengan saat training (Golden Rule Modul 14).
- Serialisasi model wajib menggunakan `joblib`.
- Validasi input wajib menolak angka non-realistis (misal: budget $\le 0$, runtime $\le 0$, tahun $< 1900$ atau $> 2030$).
- Proyek harus dapat dijalankan secara lokal dengan langkah instalasi yang jelas melalui `requirements.txt`.
- Dokumentasi `README.md` dan `TUGAS_INDIVIDU_REFLEKSI.md` harus memenuhi rubrik penilaian Modul 14 Bagian C.

## Review Focus

1. **Feature Mismatch Protection:** Input DataFrame ke model memiliki format persis `pd.DataFrame({"runtime": [...], "votes": [...], "budget": [...], "year": [...]})`.
2. **Invalid Input Handling:** Form memberikan pesan error ramah jika ada input kosong, non-numerik, atau di luar batas logis.
3. **Model Loading Efficiency:** Model `.joblib` dimuat dengan caching atau diinisialisasi sekali saat server view aktif, bukan dibaca ulang setiap kali request jika tidak diperlukan.
4. **Reproducibility:** File `requirements.txt` dan script training mandiri `train_and_export.py` memungkinkan siapa saja melatih ulang dan menjalankan aplikasi dari nol.
5. **UI & Usability:** Antarmuka memiliki nilai *default* realistis sehingga penguji/dosen dapat langsung klik tombol prediksi untuk melihat contoh hasil kerja.

---

### Task 1: Pipeline Data & Pelatihan Model ML (`ml_model/`)

**Files:**
- Create: `ml_model/movies_clean.csv` (disalin dari uploaded dataset)
- Create: `ml_model/train_and_export.py`
- Output: `ml_model/model_quality.joblib`
- Output: `ml_model/model_score.joblib`
- Output: `ml_model/model_meta.json`

- [ ] Salin dataset `movies_clean.csv` dari artefak unggahan ke folder `ml_model/`.
- [ ] Buat script `ml_model/train_and_export.py`:
  - Membersihkan data: `df.dropna(subset=['budget', 'year', 'score', 'votes', 'runtime'])` dan filter `budget > 0`.
  - Buat target klasifikasi: `kualitas` (`Kurang` < 6.0, `Bagus` 6.0-7.0, `Sangat Bagus` $\ge$ 7.0).
  - Latih `DecisionTreeClassifier(max_depth=3, random_state=42)` dengan fitur `['runtime', 'votes', 'budget', 'year']`.
  - Latih `LinearRegression()` dengan fitur `['runtime', 'votes']` untuk estimasi skor.
  - Simpan model dengan `joblib.dump(..., 'model_quality.joblib')` dan `joblib.dump(..., 'model_score.joblib')`.
  - Simpan metadata ringkasan (akurasi latih, feature importances, statistik min/max fitur) ke `model_meta.json`.
- [ ] Jalankan `python ml_model/train_and_export.py` dan verifikasi kedua file `.joblib` terbuat dan dapat dimuat kembali untuk memprediksi data uji dummy.

---

### Task 2: Inisialisasi Proyek Django & Konfigurasi Lingkungan

**Files:**
- Create: `requirements.txt`
- Create: Proyek Django `movie_system/`
- Create: Aplikasi Django `predictor/`
- Modify: `movie_system/settings.py`
- Modify: `movie_system/urls.py`

- [ ] Buat `requirements.txt` berisi dependensi: `django>=4.2`, `scikit-learn`, `pandas`, `numpy`, `joblib`.
- [ ] Instal dependensi yang diperlukan.
- [ ] Jalankan perintah inisialisasi Django:
  - `django-admin startproject movie_system .`
  - `python manage.py startapp predictor`
- [ ] Daftarkan app `'predictor'` ke `INSTALLED_APPS` di `movie_system/settings.py`.
- [ ] Konfigurasikan folder `TEMPLATES` dan `STATIC` di `movie_system/settings.py`.
- [ ] Hubungkan rute `predictor.urls` ke `movie_system/urls.py`.
- [ ] Jalankan `python manage.py migrate` dan `python manage.py check` untuk memastikan konfigurasi dasar valid.

---

### Task 3: Logika Bisnis & View Inferensi (`predictor/views.py`)

**Files:**
- Create: `predictor/forms.py`
- Create: `predictor/urls.py`
- Modify: `predictor/views.py`
- Create: `predictor/tests.py`

- [ ] Buat form `MoviePredictionForm` di `predictor/forms.py` dengan field:
  - `runtime` (Integer, menit, misal min=30, max=400, default=120)
  - `votes` (Integer, total ulasan, misal min=100, default=50000)
  - `budget` (Float/BigInteger, USD, misal min=10000, default=25000000)
  - `year` (Integer, tahun rilis, misal min=1970, max=2030, default=2022)
- [ ] Buat fungsi `load_models()` di `predictor/views.py` dengan penanganan cache/singleton agar hemat memori.
- [ ] Implementasikan view `index_view`:
  - `GET`: Menampilkan form kosong/dengan nilai default + statistik ringkasan dataset.
  - `POST`: Validasi form, ekstraksi data ke DataFrame pandas, eksekusi inferensi kualitas & estimasi skor, serta perhitungan interpretasi.
- [ ] Daftarkan URL di `predictor/urls.py` (`''` ke `index_view`).
- [ ] Buat test case di `predictor/tests.py` untuk menguji:
  - Form validasi input benar & input salah.
  - View GET mengembalikan status code 200.
  - View POST dengan data valid mengembalikan status 200 dengan hasil prediksi dalam konteks.
- [ ] Jalankan `python manage.py test predictor` dan pastikan lulus 100%.

---

### Task 4: Desain Antarmuka Pengguna Responsif (Templates Bootstrap 5)

**Files:**
- Create: `predictor/templates/predictor/base.html`
- Create: `predictor/templates/predictor/index.html`
- Create: `predictor/templates/predictor/result_partial.html` (atau blok hasil di `index.html`)

- [ ] Buat `base.html` menggunakan Bootstrap 5 CDN, ikon Bootstrap Icons, navbar profesional dengan nama proyek *"CineMetrics - Sistem Cerdas Prediksi Kualitas Film"*, dan footer identitas mahasiswa.
- [ ] Buat `index.html`:
  - Card Pengantar: Deskripsi sistem cerdas berbasis Decision Tree & Regresi Linear.
  - Card Form Input: Form 2 kolom yang rapi, label jelas, badge satuan (menit, USD, vote), dan tombol "Prediksi Film".
  - Section Panduan Fitur: Memberi konteks rentang nilai rata-rata dari dataset P07 agar user mudah mencoba.
- [ ] Buat komponen Hasil Prediksi:
  - Badge visual status kualitas (Hijau: Sangat Bagus, Biru: Bagus, Kuning/Merah: Kurang).
  - Skor estimasi numerik (IMDb scale) dengan progress bar.
  - Bar Feature Importance: Menunjukkan pengaruh masing-masing parameter (Votes, Budget, Runtime, Year) terhadap keputusan model.
  - Tombol reset/coba prediksi baru.
- [ ] Uji responsivitas halaman (desktop & mobile view) dan pastikan tidak ada error rendering template.

---

### Task 5: Dokumentasi Lengkap & Refleksi Individu (Standar Modul 14)

**Files:**
- Create: `README.md`
- Create: `TUGAS_INDIVIDU_REFLEKSI.md`

- [ ] Susun `README.md` sesuai format penilaian Bagian C Modul 14:
  - 1. Judul & Deskripsi Aplikasi (Tujuan bisnis/pengguna).
  - 2. Arsitektur Sistem Cerdas (Machine learning to Django deployment).
  - 3. Struktur Dataset & Keterangan Lisensi.
  - 4. Petunjuk Instalasi & Menjalankan Aplikasi (Langkah per langkah yang dapat direproduksi).
  - 5. Tabel Pembagian Peran Anggota Kelompok.
  - 6. Screenshot / Gambaran Antarmuka.
- [ ] Susun `TUGAS_INDIVIDU_REFLEKSI.md` untuk Sub-CPMK 0812 & 0832:
  - Bagian A: 2 topik kecerdasan buatan pilihan untuk pendalaman.
  - Bagian B: 1 rencana kursus/sertifikasi mandiri dalam 6 bulan.
  - Bagian C: 3 langkah konkret yang diambil pada bulan pertama.
- [ ] Lakukan verifikasi menyeluruh: jalankan server Django lokal `python manage.py runserver`, lakukan pengujian simulasi form, dan pastikan seluruh berkas lengkap.
