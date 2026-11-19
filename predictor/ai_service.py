import os
import json
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Muat file .env jika ada
load_dotenv()

def get_gemini_key():
    load_dotenv(override=True)
    return os.getenv("GEMINI_API_KEY", "").strip()

def _call_gemini_api(prompt: str, system_instruction: str = "") -> str:
    """Melakukan panggilan langsung ke Google Gemini REST API jika API Key tersedia."""
    api_key = get_gemini_key()
    if not api_key:
        return ""

    headers = {"Content-Type": "application/json"}
    
    contents = [{
        "role": "user",
        "parts": [{"text": prompt}]
    }]

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }

    if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    # Model kandidat yang aktif dan diverifikasi mendukung kunci API ini
    candidate_models = [
        "gemini-3.1-flash-lite",
        "gemini-3-flash-preview",
        "gemini-flash-latest",
        "gemma-4-26b-a4b-it"
    ]

    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            else:
                logger.warning("Panggilan API Gemini model %s mengembalikan status code %s", model_name, response.status_code)
        except requests.RequestException as e:
            logger.info("Koneksi Gemini model %s gagal: %s", model_name, e)
            continue
        except Exception as e:
            logger.warning("Terjadi kesalahan tidak terduga pada panggilan model %s: %s", model_name, e)
            continue

    return ""


def generate_movie_insight(runtime: int, votes: int, budget: float, year: int, kualitas: str, skor_imdb: float) -> str:
    """Menghasilkan analisis eksekutif dinamis tentang potensi performa film."""
    prompt = (
        f"Sebagai analis industri perfilman profesional dan pakar box office, berikan 2-3 kalimat analisis kritis, "
        f"tajam, dan rekomendasi strategis mengenai proyeksi film berikut:\n"
        f"- Durasi: {runtime} Menit\n"
        f"- Estimasi Votes Audiens: {votes:,}\n"
        f"- Anggaran Produksi: ${budget:,.0f} USD\n"
        f"- Tahun Rilis: {year}\n"
        f"- Klasifikasi Kualitas: {kualitas}\n"
        f"- Estimasi Skor IMDb: {skor_imdb} / 10.0\n"
        f"Gunakan Bahasa Indonesia yang elegan, profesional, dan padat makna."
    )

    ai_reply = _call_gemini_api(
        prompt, 
        system_instruction="Anda adalah konsultan eksekutif studio film global untuk platform analitik CineMetrics."
    )
    if ai_reply:
        return ai_reply

    # Smart Rule-Based Engine (Fallback Cerdas saat API Key belum dipasang / Offline)
    budget_mil = budget / 1_000_000
    if kualitas == "Sangat Bagus":
        if budget_mil > 80:
            return (
                f"Film ini menunjukkan profil Blockbuster berkinerja tinggi. Dengan anggaran ${budget_mil:.1f}M dan proyeksi resonansi "
                f"{votes:,} votes, rasio investasi terhadap penerimaan audiens sangat kuat. Durasi {runtime} menit dinilai pas "
                f"untuk mempertahankan pacing sinematik serta memaksimalkan rotasi layar bioskop global."
            )
        else:
            return (
                f"Film mencerminkan efisiensi produksi luar biasa (High-ROI). Dengan bujet terukur ${budget_mil:.1f}M, "
                f"tingginya traksi {votes:,} votes mengindikasikan potensi 'Word-of-Mouth' yang masif. Proyeksi rating {skor_imdb}/10 "
                f"menjadikannya kandidat kuat rilis festival bergengsi dan platform streaming premium."
            )
    elif kualitas == "Bagus":
        if runtime > 150:
            return (
                f"Film berada di jalur performa kompetitif dengan estimasi skor {skor_imdb}/10. Namun, durasi penayangan {runtime} menit "
                f"tergolong cukup panjang bagi penonton umum, yang berpotensi membatasi jumlah showtime harian. Disarankan optimalisasi "
                f"editing dan penguatan kampanye pemasaran digital untuk menjaga retensi audiens."
            )
        else:
            return (
                f"Prospek penerimaan audiens stabil dengan traksi {votes:,} ulasan. Alokasi bujet ${budget_mil:.1f}M "
                f"berada dalam zona aman untuk film berdurasi {runtime} menit. Fokus pada strategi distribusi multi-platform dan "
                f"penjadwalan rilis di luar persaingan film raksasa akan mengoptimalkan keuntungan komersial."
            )
    else:
        return (
            f"Film terproyeksi berada di zona underperforming dengan skor {skor_imdb}/10. Dengan anggaran ${budget_mil:.1f}M, "
            f"volume resonansi pasar ({votes:,} votes) relatif belum cukup untuk menjamin titik impas bioskop. Disarankan "
            f"evaluasi ulang penargetan demografi audiens dan penyesuaian strategi promosi sebelum rilis resmi."
        )


def is_out_of_scope(message: str) -> bool:
    """Mendeteksi apakah pertanyaan berada di luar domain perfilman dan sistem CineMetrics."""
    msg = message.lower().strip()
    
    # Kata kunci terlarang yang jelas di luar konteks perfilman dan platform CineMetrics
    forbidden_topics = [
        "resep", "masak", "goreng", "memasak", "bumbu", "dapur", "kue", "makanan", "minuman", "restoran", "kuliner",
        "cuaca", "ramalan cuaca", "hujan", "gempa", "angin", "iklim",
        "politik", "pemilu", "presiden", "pilpres", "pilkada", "partai", "dpr", "menteri", "pemda",
        "penyakit", "gejala", "obat", "dokter", "medis", "kanker", "flu", "rumah sakit",
        "kalkulus", "rumus fisika", "kimia", "integral", "diferensial", "aljabar",
        "lirik lagu", "chord gitar", "kunci gitar", "tab gitar",
        "pantun", "puisi", "dongeng", "cerpen",
        "crypto", "bitcoin", "forex", "trading saham", "slot", "judi"
    ]

    # Konteks perfilman dan platform yang valid
    film_context = [
        "film", "movie", "bioskop", "cinema", "cinemetrics", "rating", "imdb", "box office", 
        "aktor", "aktris", "sutradara", "genre", "produser", "durasi", "runtime", "anggaran", 
        "budget", "vote", "ulasan", "decision tree", "regresi", "machine learning", "dataset", 
        "model", "skenario", "kurang", "bagus", "sangat bagus", "prediksi"
    ]

    # Jika mengandung kata makanan/resep eksplisit, tolak langsung meskipun ada kata film
    if any(f in msg for f in ["resep", "nasi goreng", "cara masak", "cara memasak", "bumbu", "buat kue"]):
        return True

    # Jika terdeteksi topik terlarang dan tidak ada relevansi film
    if any(f in msg for f in forbidden_topics):
        if not any(fc in msg for fc in film_context):
            return True

    return False


def out_of_scope_message() -> str:
    """Pesan penolakan sopan untuk pertanyaan di luar konteks."""
    return (
        "Mohon maaf, saya adalah **CineBot**, asisten analitik khusus platform **CineMetrics AI** "
        "yang diprogram eksklusif untuk melayani konsultasi **industri perfilman** dan **analitik performa box office** di platform ini.\n\n"
        "Saya tidak dapat menjawab pertanyaan di luar konteks perfilman atau cara kerja platform ini.\n\n"
        "**Topik yang dapat Anda tanyakan:**\n"
        "• Analisis parameter film yang sedang Anda atur di slider saat ini.\n"
        "• Cara kerja model *Decision Tree* dan *Regresi Linear* di web ini.\n"
        "• Alasan volume vote audiens lebih dominan (68.3%) daripada anggaran produksi (12.7%).\n"
        "• Strategi mengatasi dan menaikkan status film dari *'Kurang'* menjadi *'Bagus'* atau *'Sangat Bagus'*."
    )


def ask_cinebot(message: str, current_context: dict = None) -> str:
    """Menjawab pertanyaan seputar website CineMetrics, model ML, dan parameter film."""
    # Guardrail langsung: cegah pertanyaan di luar konteks
    if is_out_of_scope(message):
        return out_of_scope_message()

    context_str = ""
    if current_context:
        rt = current_context.get("runtime", 120)
        vt = current_context.get("votes", 150000)
        bg = float(current_context.get("budget", 35000000))
        yr = current_context.get("year", 2021)
        kualitas = current_context.get("kualitas", "")
        skor = current_context.get("skor_imdb", "")

        context_str = (
            f"DATA PARAMETER FILM AKTIF PENGGUNA:\n"
            f"- Durasi: {rt} menit (Standar dataset: ~107 menit)\n"
            f"- Votes Audiens: {vt:,} ulasan\n"
            f"- Anggaran: ${bg:,.0f} USD\n"
            f"- Tahun Rilis: {yr}\n"
        )
        if kualitas and kualitas != "-":
            context_str += f"- Hasil Prediksi Kualitas: {kualitas}\n"
        if skor and skor != "0.0":
            context_str += f"- Estimasi Skor Rating IMDb: {skor} / 10.0\n"

    system_prompt = (
        "Anda adalah 'CineBot', asisten virtual intelijen sinema dan pakar analitik data film untuk platform CineMetrics AI. "
        "PERAN UTAMA: Menjelaskan industri perfilman global, metrik box office, arsitektur Machine Learning (Decision Tree dan Regresi Linear), "
        "serta memberikan konsultasi analisis film berdasarkan parameter yang diatur pengguna.\n\n"
        "BATASAN DOMAIN KETAT (STRICT GUARDRAILS):\n"
        "1. Anda HANYA diperbolehkan menjawab pertanyaan yang berhubungan dengan: dunia perfilman/sinema/box office/produksi film, "
        "atau cara kerja sistem dan model Machine Learning di website CineMetrics ini.\n"
        "2. JIKA PENGGUNA BERTANYA DI LUAR KONTEKS PERFILMAN ATAU DI LUAR WEBSITE INI (seperti resep makanan, masakan, politik, cuaca, matematika umum, koding umum, dll.): "
        "ANDA DILARANG KERAS MENJAWABNYA. Tolak secara sopan dan tegas, katakan bahwa Anda adalah CineBot khusus perfilman, lalu ajak kembali ke analisis film.\n\n"
        "PENGETAHUAN MODEL CINEMETRICS:\n"
        "- Decision Tree Classifier (max_depth=3) untuk Kualitas (Kurang < 6.0, Bagus 6.0 s.d < 7.0, Sangat Bagus >= 7.0)\n"
        "- Linear Regression untuk skor kontinu IMDb (1.0 - 10.0)\n"
        "- Bobot Variabel: Votes Audiens (68.3% - Terbesar), Durasi Runtime (19.0%), Anggaran/Budget (12.7%), Tahun Rilis (0.0%)\n"
        "- Dataset: 5.421 film bioskop global hasil kurasi terstandarisasi\n"
        "- Jika pengguna bertanya cara mengatasi film yang 'Kurang' (atau typo 'kalsifikasi kuliatas'): sarankan naikkan durasi ke 105-120 menit dan targetkan votes > 100.000, serta jelaskan bahwa menambah anggaran saja (bobot 12.7%) tidak akan efektif jika durasi dan ulasan minim."
    )

    full_prompt = f"{context_str}\nPertanyaan Pengguna: {message}"
    ai_reply = _call_gemini_api(full_prompt, system_instruction=system_prompt)
    if ai_reply:
        return ai_reply

    # Smart Knowledge Base Fallback jika tanpa API Key / Offline
    msg = message.lower()

    if any(k in msg for k in ["kurang", "mengatasi", "menaikkan", "naikkan", "perbaiki", "tingkatkan"]):
        return (
            "Untuk mengatasi film yang masuk klasifikasi **'Kurang'** agar naik ke kategori **'Bagus'** atau **'Sangat Bagus'**, "
            "perhatikan bobot faktor penentu pada model Decision Tree CineMetrics:\n\n"
            "1. **Tingkatkan Resonansi Votes (Bobot 68.3% - Faktor Terbesar):**\n"
            "   Tingkatkan target antusiasme audiens hingga di atas **100.000 votes**. Volume ulasan adalah penentu terbesar apakah film berhasil menembus pasar luas.\n\n"
            "2. **Optimalisasi Durasi Film (Bobot 19.0%):**\n"
            "   Jika durasi film Anda saat ini di bawah 90 menit (misal 70–80 menit), model cenderung menilai penceritaan kurang mendalam. Naikkan durasi ke rentang ideal bioskop **105 – 120 menit**.\n\n"
            "3. **Perhatikan Efisiensi Anggaran (Bobot 12.7%):**\n"
            "   Menambah modal/anggaran besar saja **tidak akan otomatis membuat film jadi Bagus** jika durasi terlalu pendek atau ulasan minim. Alokasikan anggaran untuk kualitas teknis dan pemasaran yang memicu ulasan positif penonton.\n\n"
            "Silakan geser slider durasi dan vote di samping, lalu klik *Jalankan Inferensi Model* untuk melihat perubahannya!"
        )

    if any(k in msg for k in ["cara kerja", "bagaimana web ini", "sistem ini", "website ini"]):
        return (
            "Platform **CineMetrics** bekerja dengan mengintegrasikan dua model Machine Learning ke dalam arsitektur analitik web:\n"
            "1. **Klasifikasi Kualitas (Decision Tree):** Menilai apakah film masuk kategori *Kurang*, *Bagus*, atau *Sangat Bagus* "
            "berdasarkan durasi, vote, anggaran, dan tahun.\n"
            "2. **Estimasi Rating (Regresi Linear):** Memproyeksikan skor kontinu IMDb (skala 1.0–10.0) berbasis durasi dan volume vote.\n\n"
            "Anda dapat mengatur slider di sebelah kiri, dan sistem akan langsung memberikan evaluasi serta wawasan prediktif secara instan!"
        )

    if any(k in msg for k in ["decision tree", "pohon keputusan", "klasifikasi"]):
        return (
            "Model **Decision Tree Classifier** (dengan batas kedalaman `max_depth=3`) digunakan untuk klasifikasi kualitas film. "
            "Model ini membuat keputusan hierarkis seperti pohon logika untuk membagi film ke dalam 3 tier:\n"
            "- **Kurang:** Skor < 6.0\n"
            "- **Bagus:** Skor 6.0 s.d. < 7.0\n"
            "- **Sangat Bagus:** Skor ≥ 7.0\n"
            "Fitur yang paling dominan mempengaruhi pohon keputusan ini adalah **volume vote audiens** (bobot ~68.3%)."
        )

    if any(k in msg for k in ["regresi", "linear regression", "skor", "rating"]):
        return (
            "Model **Linear Regression** digunakan untuk memprediksi angka kontinu skor rating IMDb. "
            "Model dilatih menggunakan fitur `runtime` (durasi) dan `votes` (jumlah ulasan). "
            "Secara matematis, semakin tinggi volume vote audiens yang organik dengan durasi yang optimal, "
            "semakin tinggi estimasi skor film yang diproyeksikan."
        )

    if any(k in msg for k in ["vote", "bobot", "pengaruh", "anggaran", "budget"]):
        return (
            "Berdasarkan analisis empiris dataset 5.400+ film historis IMDb, **Volume Vote (68.3%)** jauh lebih berpengaruh daripada **Anggaran (12.7%)**. "
            "Hal ini karena anggaran besar tidak menjamin sebuah film disukai penonton, sedangkan jumlah vote ulasan yang tinggi "
            "adalah bukti nyata antusiasme dan penerimaan positif audiens di pasar global."
        )

    if any(k in msg for k in ["dataset", "data", "sumber", "5400"]):
        return (
            "Dataset yang digunakan adalah *Movie Industry Dataset* (IMDb Public Benchmark Data) yang telah dikurasi "
            "dan distandarisasi dalam korpus analitik CineMetrics. Berisi **5.421 film** dengan kelengkapan data durasi, anggaran (budget > 0), "
            "tahun rilis, skor rating, dan volume ulasan pengguna."
        )

    if any(k in msg for k in ["analisis", "parameter", "film saya", "film ini", "skenario", "atur", "prospek"]):
        if current_context:
            rt = current_context.get("runtime", 120)
            vt = current_context.get("votes", 150000)
            bg = float(current_context.get("budget", 35000000))
            yr = current_context.get("year", 2021)
            return (
                f"**Analisis Parameter Film Aktif:**\n"
                f"• Durasi: **{rt} Menit** (Standar umum: ~107 menit)\n"
                f"• Target Votes: **{vt:,} Ulasan Audiens**\n"
                f"• Anggaran: **${bg:,.0f} USD**\n"
                f"• Tahun Rilis: **{yr}**\n\n"
                f"Kombinasi parameter ini menunjukkan daya tarik yang menarik. Klik tombol **'Analisis & Prediksi Film'** "
                f"untuk melihat proyeksi tier klasifikasi (Decision Tree) dan estimasi skor rating IMDb secara lengkap!"
            )
        return "Silakan geser slider parameter film di sisi kiri, dan saya akan membantu menganalisis kelayakannya!"

    return (
        "Halo! Saya **CineBot**, asisten cerdas CineMetrics. "
        "Saya dapat membantu menjelaskan cara kerja model Decision Tree & Regresi, pengaruh variabel pasar, "
        "atau menganalisis parameter film yang sedang Anda rancang. Ada yang ingin Anda tanyakan seputar sistem ini?"
    )
