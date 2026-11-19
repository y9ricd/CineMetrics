# Gemini AI Live Analysis & Cinema ChatBot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mengintegrasikan analisis film generatif langsung menggunakan Gemini API (bukan template statis) serta menambahkan widget AI ChatBot interaktif ("CineBot") yang dapat menjelaskan website, cara kerja model (Decision Tree & Regresi Linear), dan menjawab pertanyaan dosen/pengguna secara cerdas.

**Architecture:**
- Backend: Modul `predictor/ai_service.py` untuk mengelola interaksi ke Google Gemini API via `requests` dengan integrasi `.env` (`python-dotenv`). Mengimplementasikan *Dual-Engine Architecture* (Live Gemini API + Smart Fallback Knowledge Base) agar sistem 100% tahan banting jika offline/tanpa API key.
- Endpoint Chat: `POST /api/chat/` menerima pesan user dan data parameter film aktif, mengembalikan respons asisten sinematik.
- Dynamic Insight: `POST /` (atau saat request prediksi) menghasilkan narasi analisis mendalam dari AI khusus untuk kombinasi metrik pengguna.
- Frontend: Widget floating ChatBot di pojok kanan bawah dengan palet `#1B191A`, `#E9E4E0`, `#943A1F`, quick suggestion chips, typing indicator, dan efek typewriter pada kotak Ringkasan Analisis AI.

**Tech Stack:** Django, Python, `requests`, `python-dotenv`, Bootstrap 5, Bootstrap Icons, Vanilla JS.

---

### Task 1: Modul AI Service (`predictor/ai_service.py`) & Pengujian Unit Test

**Files:**
- Create: `predictor/ai_service.py`
- Modify: `predictor/tests.py`

**Interfaces:**
- `generate_movie_insight(runtime, votes, budget, year, kualitas, skor_imdb) -> str`
- `ask_cinebot(message, current_context=None) -> str`

- [x] **Step 1: Tulis unit test untuk `ai_service`**
  Uji bahwa fungsi `generate_movie_insight` dan `ask_cinebot` selalu mengembalikan string non-kosong yang relevan, baik saat API key ada maupun saat fallback aktif.

- [x] **Step 2: Jalankan test untuk memverifikasi test awal (RED)**

- [x] **Step 3: Implementasikan `predictor/ai_service.py`**
  - Baca `GEMINI_API_KEY` dari environment/`.env`.
  - Panggilan REST API Gemini `v1beta/models/gemini-1.5-flash:generateContent`.
  - Smart Knowledge Base Fallback dengan konteks arsitektur Tugas Akhir Modul 14 (P07 dataset 5.421 film, Decision Tree max_depth=3, Linear Regression, feature sensitivity).

- [x] **Step 4: Jalankan test dan pastikan lulus (GREEN)**

---

### Task 2: Integrasi Endpoint Chat & Analisis Dinamis di `views.py` & `urls.py`

**Files:**
- Modify: `predictor/urls.py`
- Modify: `predictor/views.py`
- Modify: `predictor/tests.py`

**Interfaces:**
- URL: `path("api/chat/", views.chat_view, name="chat")`
- Method: `POST` (menerima JSON atau form-data `message`, `runtime`, `votes`, `budget`, `year`)
- Return: `JsonResponse({"success": True, "reply": str, "source": "gemini"|"smart_fallback"})`

- [x] **Step 1: Tambahkan test endpoint `chat_view` di `predictor/tests.py`**
- [x] **Step 2: Tambahkan rute URL di `predictor/urls.py`**
- [x] **Step 3: Implementasikan `chat_view` dan hubungkan `generate_movie_insight` di `index_view`**
- [x] **Step 4: Jalankan unit testing Django**

---

### Task 3: Antarmuka ChatBot Sinematik & Typewriter Effect di `index.html`

**Files:**
- Modify: `predictor/templates/predictor/index.html`

**Interfaces:**
- Floating button ChatBot di pojok kanan bawah dengan warna `#943A1F` dan icon robot/chat.
- Modal/Drawer Chat pop-up dengan glassmorphism & palet `#1B191A`, `#E9E4E0`.
- Quick questions chips ("Bagaimana cara kerja model ini?", "Jelaskan pengaruh vote", dll).
- Typewriter animation untuk kotak analisis film.

- [x] **Step 1: Tambahkan markup HTML & CSS ChatBot di `index.html`**
- [x] **Step 2: Implementasikan script interaktif untuk ChatBot (buka/tutup, kirim pesan, auto-scroll, chips click)**
- [x] **Step 3: Hubungkan efek typewriter pada kotak Ringkasan Analisis AI**

---

### Task 4: Pengujian & Konfigurasi `.env`

**Files:**
- Create: `.env.example`
- Verifikasi: `.\venv\Scripts\python.exe manage.py test predictor`
- Verifikasi: Rendering halaman & integrasi endpoint chat
