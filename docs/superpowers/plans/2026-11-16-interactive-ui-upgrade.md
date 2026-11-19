# Interactive UI & Cinema Color Palette Upgrade Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Meng-upgrade antarmuka web CineMetrics menjadi interaktif dengan animasi halus, menerapkan palet warna baru (`#1B191A`, `#E9E4E0`, `#943A1F`), membersihkan catatan/debug yang tidak perlu, dan menyediakan dual-slider serta respons prediksi instan (AJAX) tanpa reload.

**Architecture:** Model Scikit-Learn tetap berjalan di backend Django (`views.py`). `index_view` diperkaya agar dapat mengembalikan respons JSON ketika dipanggil via AJAX/Fetch API tanpa mengorbankan form submit tradisional. Template `base.html` dan `index.html` dirombak menggunakan CSS variables palet baru, dual input (slider + number sync), preset skenario interaktif, dan animasi JavaScript murni (rolling counter, bar fill, card entrance).

**Tech Stack:** Django 6 / Python, Bootstrap 5, Bootstrap Icons, Vanilla JS (Fetch API, DOM animation), CSS3 Animations.

**Spec:** Permintaan pengguna untuk web interaktif beranimasi, main color `#1B191A`, `#E9E4E0`, `#943A1F`, serta penghapusan catatan/clutter yang tidak perlu.

## Global Constraints

- Warna dominan wajib: `#1B191A` (Dark Charcoal/Obsidian), `#E9E4E0` (Alabaster Cream), `#943A1F` (Terracotta Accent).
- Form submission standar (POST non-AJAX) harus tetap berfungsi 100% dan seluruh 5 unit tests Django yang ada harus tetap lolos.
- Hilangkan teks debug ("Status Evaluasi: Verified (200 OK)"), catatan teknis akademis berlebihan, dan simplifikasi tampilan agar bersih dan profesional.
- Tidak boleh merusak model machine learning (`model_quality.joblib` dan `model_score.joblib`).

## Review Focus

1. **Dual Slider-Input Sync:** Mengubah slider otomatis mengubah kotak angka dan sebaliknya; nilai tetap terkirim dengan benar pada form POST.
2. **AJAX vs Standard POST Fallback:** Permintaan AJAX via Fetch mengembalikan JSON yang merender kartu hasil secara dinamis, sementara submit biasa tanpa JS tetap merender template Django seperti biasa.
3. **Contrast & Readability:** Teks di atas warna `#1B191A`, `#E9E4E0`, dan `#943A1F` harus memenuhi standar keterbacaan (rasio kontras tinggi).
4. **Animation Performance:** Animasi counter skor dan progress bar berjalan mulus 60fps tanpa layout shift yang mengganggu.
5. **Preset Scenario Validation:** Mengklik preset (Blockbuster, Indie, Drama) langsung memperbarui slider dan form input dengan nilai valid.

---

### Task 1: Dukungan Endpoint AJAX di `predictor/views.py` & Penambahan Unit Test

**Files:**
- Modify: `predictor/views.py`
- Modify: `predictor/tests.py`

**Interfaces:**
- Produces: `JsonResponse` ketika request menyertakan header `x-requested-with: XMLHttpRequest` atau parameter `ajax=1`. Format: `{"success": true, "result": {...}}` atau `{"success": false, "errors": {...}}`.

- [x] **Step 1: Tulis unit test untuk verifikasi endpoint AJAX**
  Tambahkan method `test_index_view_ajax_prediction` di `predictor/tests.py` yang mengirim request POST dengan header `HTTP_X_REQUESTED_WITH="XMLHttpRequest"` dan memverifikasi status 200 dengan format JSON.

- [x] **Step 2: Jalankan test untuk memverifikasi test awal**
  Jalankan: `.\venv\Scripts\python.exe manage.py test predictor`
  Verifikasi hasilnya.

- [x] **Step 3: Update `predictor/views.py` dengan penanganan JSON response**
  Jika `request.headers.get('x-requested-with') == 'XMLHttpRequest'` atau `request.POST.get('ajax') == '1'`, kembalikan `JsonResponse` berisi dictionary `result`.

- [x] **Step 4: Jalankan test kembali dan pastikan lulus 100%**
  Jalankan: `.\venv\Scripts\python.exe manage.py test predictor`
  Expected: 6 test lulus tanpa error.

---

### Task 2: Refactor Template Induk `predictor/templates/predictor/base.html`

**Files:**
- Modify: `predictor/templates/predictor/base.html`

**Interfaces:**
- Menetapkan CSS variables untuk `#1B191A`, `#E9E4E0`, `#943A1F`.
- Menyederhanakan header navbar: tema bioskop premium, menghapus badge berlebih.
- Menambahkan styling animasi global (`@keyframes fadeInUp`, `@keyframes pulseGlow`, `@keyframes shimmer`).
- Footer rapi dan elegan tanpa catatan yang berantakan.

- [x] **Step 1: Perbarui CSS variabel dan aturan dasar di `base.html`**
  Tetapkan `--color-obsidian: #1B191A`, `--color-cream: #E9E4E0`, `--color-terracotta: #943A1F`, `--color-terracotta-hover: #7d2f17`.
  Terapkan warna latar kanvas `#E9E4E0` dan teks utama `#1B191A`.

- [x] **Step 2: Bersihkan navbar dan footer**
  Ubah background navbar ke `#1B191A`, tombol dan aksen menggunakan `#943A1F`. Bersihkan badge internal yang tidak perlu.

- [x] **Step 3: Verifikasi sintaks template dan pastikan tidak ada tag rusak**

---

### Task 3: Overhaul `predictor/templates/predictor/index.html` dengan Interaktivitas & Animasi

**Files:**
- Modify: `predictor/templates/predictor/index.html`

**Interfaces:**
- Input ganda: Slider sinkron dengan Number Input (Runtime, Votes, Budget, Year).
- Quick Scenario Presets: Tombol pill "Blockbuster", "Indie Film", "Mid-Budget Drama", "Cult Classic".
- Animasi: Counter angka skor IMDb (0.0 -> skor), animasi pengisian bar persentase, kartu hasil muncul dengan fade-in & slide-up.
- Asynchronous Submission: Form submit menggunakan JavaScript Fetch API untuk memperbarui kartu hasil secara instan dengan indikator loading animasi halus, tanpa reload layar.
- Pembersihan Catatan: Hapus "Status Evaluasi: Verified (200 OK)", label debug modul, dan gantikan dengan visual badge yang bersih.

- [x] **Step 1: Rancang ulang tata letak form dengan Dual-Slider + Quick Presets**
  Tambahkan slider `<input type="range">` di bawah masing-masing input number dengan event listener sinkronisasi dua arah.
  Tambahkan tombol-tombol preset cepat di bagian atas form.

- [x] **Step 2: Rancang ulang kartu hasil dengan estetika palet baru & container dinamis**
  Buat elemen wrapper hasil prediksi yang dapat dirender baik dari context server (saat fallback submit standar) maupun via JavaScript AJAX.
  Gunakan badge warna terintegrasi dengan aksen `#943A1F`.

- [x] **Step 3: Implementasikan skrip JavaScript interaktif**
  - Sinkronisasi slider <-> number input live.
  - Event listener untuk tombol preset yang mengupdate semua field sekaligus.
  - Async submit handler via `fetch()` ke URL prediksi dengan CSRF token.
  - Animasi rolling score counter (ease-out dari 0 ke target).
  - Animasi progress bar.

---

### Task 4: Pengujian Menyeluruh (Automated Tests & Manual Verification)

**Files:**
- Verifikasi: `predictor/tests.py`
- Verifikasi: Halaman web via server Django

- [x] **Step 1: Jalankan unit testing Django**
  Jalankan `.\venv\Scripts\python.exe manage.py test predictor`
  Pastikan seluruh test lulus.

- [x] **Step 2: Jalankan Django system checks**
  Jalankan `.\venv\Scripts\python.exe manage.py check`
  Pastikan 0 error / issues.
