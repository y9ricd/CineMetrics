import os
import json
from pathlib import Path
import streamlit as st
import pandas as pd
import joblib

# Muat modul AI service lokal
from predictor.ai_service import generate_movie_insight, ask_cinebot

# ==========================================
# KONFIGURASI HALAMAN ENTERPRISE
# ==========================================
st.set_page_config(
    page_title="CineMetrics AI — Enterprise Film Intelligence Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Injection: Linear / Stripe Enterprise Aesthetic (Anti-AI Slop)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Sembunyikan elemen default Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    :root {
        --accent: #9A3412;
        --border-subtle: #E6E1D8;
        --bg-subtle: #F5F3EF;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        letter-spacing: -0.01em;
    }

    /* Tabular Font untuk Metrik & Data */
    .stMetric [data-testid="stMetricValue"], 
    .stMetric [data-testid="stMetricDelta"],
    code, pre, .font-mono {
        font-family: 'JetBrains Mono', monospace !important;
        font-feature-settings: 'tnum' on, 'zero' on !important;
    }

    /* Heading styling */
    h1, h2, h3, h4 {
        letter-spacing: -0.02em !important;
        font-weight: 700 !important;
    }

    /* Tombol Utama Enterprise */
    .stButton > button {
        border-radius: 0.375rem !important;
        font-weight: 600 !important;
        font-size: 0.8125rem !important;
        letter-spacing: -0.01em !important;
        transition: all 0.15s ease !important;
    }

    /* Technical Category Labels */
    .tech-pill {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #71717A;
        background: #F4F1EA;
        border: 1px solid #E6E1D8;
        padding: 0.15rem 0.5rem;
        border-radius: 0.25rem;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }

    .memo-box {
        background-color: #FAF9F6;
        border: 1px solid #E6E1D8;
        border-left: 3px solid #9A3412;
        padding: 1rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        line-height: 1.6;
        color: #3F3F46;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Path Aset
BASE_DIR = Path(__file__).resolve().parent
ML_DIR = BASE_DIR / "ml_model"

@st.cache_resource
def muat_model():
    """Memuat model biner Scikit-learn (Joblib) dan metadata sekali saja ke memori."""
    clf_path = ML_DIR / "model_quality.joblib"
    reg_path = ML_DIR / "model_score.joblib"
    meta_path = ML_DIR / "model_meta.json"

    if not clf_path.exists() or not reg_path.exists():
        st.error(f"File model tidak ditemukan di {ML_DIR}. Harap latih model terlebih dahulu.")
        st.stop()

    clf = joblib.load(clf_path)
    reg = joblib.load(reg_path)

    meta = {}
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

    return clf, reg, meta

@st.cache_data
def muat_dataset_summary():
    """Memuat dan mengagregasi dataset 5.421 film IMDb untuk visualisasi data analitik."""
    csv_path = ML_DIR / "movies_clean.csv"
    if not csv_path.exists():
        return None, None
    try:
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["runtime", "votes", "budget", "year", "score"])
        df = df[df["budget"] > 0].copy()
        df["kualitas"] = pd.cut(
            df["score"],
            bins=[0, 6.0, 7.0, 11.0],
            right=False,
            labels=["Kurang", "Bagus", "Sangat Bagus"]
        ).astype(str)
        
        # Agregasi Skor per Kualitas
        df_kualitas = df.groupby("kualitas")["score"].mean().round(2).reindex(["Kurang", "Bagus", "Sangat Bagus"])
        
        # Agregasi Skor per Top 7 Genre
        top_genres = df["genre"].value_counts().head(7).index
        df_genre = df[df["genre"].isin(top_genres)].groupby("genre")["score"].mean().sort_values(ascending=False).round(2)
        
        return df_kualitas, df_genre
    except Exception:
        return None, None

# Muat model & dataset
clf, reg, meta = muat_model()
df_kualitas_agg, df_genre_agg = muat_dataset_summary()

# ==========================================
# HEADER & DESKRIPSI UTAMA (ENTERPRISE)
# ==========================================
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown('<span class="tech-pill">ANALYTICS ENGINE</span><span class="tech-pill">ENTERPRISE EDITION</span>', unsafe_allow_html=True)
    st.title("Film Quality & IMDb Rating Forecaster")
    st.caption(
        "Dual-model predictive pipeline: Decision Tree quality classification & Linear Regression IMDb estimation "
        "trained on 5,421 validated theatrical releases · CineMetrics Intelligence Systems"
    )

with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E6E1D8; border-radius: 0.5rem; padding: 0.6rem 0.8rem; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;">
            <div style="color: #71717A; font-size: 0.65rem;">ENGINE STATUS</div>
            <div style="font-weight: 700; color: #15803D;">● ONLINE (DT-C3 + LR)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<hr style='margin: 0.8rem 0 1.5rem 0; border: none; border-top: 1px solid #E6E1D8;'>", unsafe_allow_html=True)

# ==========================================
# SIDEBAR / PANEL INPUT PARAMETER
# ==========================================
with st.sidebar:
    st.markdown('<span class="tech-pill">INPUT VECTOR (X)</span>', unsafe_allow_html=True)
    st.markdown("### Konfigurasi Parameter")
    st.caption("Atur metrik teknis atau pilih skenario preset:")

    # Skenario Cepat (Presets)
    preset = st.selectbox(
        "Pilih Skenario Cepat (Preset):",
        ["Mid-Budget (Default)", "Blockbuster (Tentpole)", "Indie Acclaimed (Festival)", "Low Resonance (Niche)"]
    )

    # Nilai default awal
    def_runtime = 118
    def_votes = 125000
    def_budget = 35000000
    def_year = 2022

    if preset == "Blockbuster (Tentpole)":
        def_runtime, def_votes, def_budget, def_year = 145, 520000, 180000000, 2023
    elif preset == "Mid-Budget (Default)":
        def_runtime, def_votes, def_budget, def_year = 118, 125000, 35000000, 2022
    elif preset == "Indie Acclaimed (Festival)":
        def_runtime, def_votes, def_budget, def_year = 102, 65000, 5000000, 2021
    elif preset == "Low Resonance (Niche)":
        def_runtime, def_votes, def_budget, def_year = 85, 8500, 40000000, 2020

    # Input Komponen Streamlit
    runtime = st.slider("Durasi Film (Runtime, Menit)", min_value=30, max_value=240, value=def_runtime, step=1)
    votes = st.slider("Proyeksi Resonansi Penonton (Votes)", min_value=500, max_value=1000000, value=def_votes, step=1000)
    budget = st.number_input(
        "Anggaran Produksi (Budget USD $)", 
        min_value=10000, 
        max_value=300000000, 
        value=def_budget, 
        step=500000,
        format="%d"
    )
    year = st.slider("Periode Rilis (Release Year)", min_value=1980, max_value=2030, value=def_year, step=1)

    st.markdown(
        f"""
        <div style="background: #F4F1EA; border: 1px solid #E6E1D8; border-radius: 0.375rem; padding: 0.5rem 0.75rem; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; margin-top: 0.75rem;">
            BUDGET_USD: <strong>${budget:,.0f}</strong><br>
            SAMPLE_TARGET: <strong>{year} THEATRICAL</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# INFERENSI MACHINE LEARNING (GOLDEN RULE)
# ==========================================
data_klasifikasi = pd.DataFrame([{
    "runtime": runtime,
    "votes": votes,
    "budget": budget,
    "year": year
}])

data_regresi = pd.DataFrame([{
    "runtime": runtime,
    "votes": votes
}])

# 1. Prediksi Klasifikasi Kualitas (Decision Tree)
pred_kualitas = clf.predict(data_klasifikasi)[0]

# Probabilitas per kelas
class_probs = {}
if hasattr(clf, "predict_proba"):
    probs = clf.predict_proba(data_klasifikasi)[0]
    for c_name, p in zip(clf.classes_, probs):
        class_probs[c_name] = round(float(p) * 100, 1)

# 2. Prediksi Skor IMDb (Regresi Linear)
pred_skor_raw = float(reg.predict(data_regresi)[0])
pred_skor = max(1.0, min(10.0, round(pred_skor_raw, 2)))

# ==========================================
# LAYOUT UTAMA: HASIL & VISUALISASI
# ==========================================
col_hasil, col_grafik = st.columns([3, 2], gap="large")

with col_hasil:
    with st.container(border=True):
        st.markdown('<span class="tech-pill">INFERENCE OUTPUT</span>', unsafe_allow_html=True)
        st.markdown("### Hasil Prediksi Model")

        # Kartu Hasil Utama (Split Metrics)
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(
                label="Klasifikasi Kualitas (Decision Tree)",
                value=pred_kualitas,
                delta="Ambang: <6.0 | 6-7 | ≥7.0"
            )

        with m_col2:
            st.metric(
                label="Estimasi Rating IMDb (Regresi Linear)",
                value=f"{pred_skor:.1f} / 10.0",
                delta=f"Skor Relatif: {pred_skor*10:.0f}%"
            )

        st.markdown("<hr style='margin: 0.5rem 0 1rem 0; border: none; border-top: 1px solid #E6E1D8;'>", unsafe_allow_html=True)

        # Distribusi Probabilitas
        st.markdown('<div class="tech-label" style="font-size: 0.6875rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 600; color: #71717A; margin-bottom: 0.5rem;">KEYAKINAN KELAS (CLASS PROBABILITY)</div>', unsafe_allow_html=True)
        prob_cols = st.columns(len(class_probs))
        for i, (kelas, prob) in enumerate(class_probs.items()):
            with prob_cols[i]:
                st.metric(label=kelas, value=f"{prob}%")

    # Executive AI Insight Container
    with st.container(border=True):
        st.markdown('<span class="tech-pill">EXECUTIVE ADVISORY</span>', unsafe_allow_html=True)
        st.markdown("### Analisis Strategis Eksekutif")
        
        with st.spinner("AI menganalisis data film..."):
            ai_insight = generate_movie_insight(
                runtime=runtime,
                votes=votes,
                budget=budget,
                year=year,
                kualitas=pred_kualitas,
                skor_imdb=pred_skor
            )
        
        st.markdown(f'<div class="memo-box">{ai_insight}</div>', unsafe_allow_html=True)

with col_grafik:
    with st.container(border=True):
        st.markdown('<span class="tech-pill">DATASET ANALYTICS</span><span class="tech-pill">HISTORICAL CORPUS</span>', unsafe_allow_html=True)
        st.markdown("### Visualisasi Grafik Data Film")
        st.caption("Eksplorasi data 5.421 film IMDb dan analisis bobot fitur model:")

        # Tab Visualisasi Grafik
        tab_chart1, tab_chart2, tab_chart3 = st.tabs(["📊 Bobot Variabel", "🏆 Top Genre", "📈 Skor Kualitas"])

        with tab_chart1:
            st.write("**Sensitivitas Fitur (Decision Tree):**")
            df_importance = pd.DataFrame({
                "Variabel": ["Votes Audiens", "Durasi Film", "Anggaran (USD)", "Tahun Rilis"],
                "Pengaruh (%)": [68.5, 25.3, 6.2, 0.0]
            }).set_index("Variabel")
            st.bar_chart(df_importance, color="#9A3412")
            st.caption("📌 **Temuan Empiris:** Volume ulasan audiens (68.5%) jauh lebih menentukan tier film dibanding anggaran (6.2%).")

        with tab_chart2:
            st.write("**Rata-rata Rating IMDb per Top Genre:**")
            if df_genre_agg is not None:
                st.bar_chart(df_genre_agg, color="#9A3412")
                st.caption("📌 **Temuan Empiris:** Genre Biography (7.09) dan Drama (6.72) mencatat rata-rata rating tertinggi.")
            else:
                st.info("Data genre dimuat dari dataset terbuka.")

        with tab_chart3:
            st.write("**Rata-rata Skor per Tier Kualitas:**")
            if df_kualitas_agg is not None:
                st.bar_chart(df_kualitas_agg, color="#78716C")
                st.caption("📌 **Ambang Batas Tier:** Kurang (<6.0, rerata 5.23), Bagus (6-7, rerata 6.45), Sangat Bagus (≥7.0, rerata 7.46).")
            else:
                st.info("Data kualitas dimuat dari dataset terbuka.")

# ==========================================
# CINEBOT: ASISTEN CHATBOT INTERAKTIF
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown('<span class="tech-pill">SYSTEM ASSISTANT</span>', unsafe_allow_html=True)
    st.markdown("### CineBot AI — Tanya Jawab Model & Industri Perfilman")
    st.caption("Konsultasikan parameter aktif Anda atau tanyakan prinsip kerja Decision Tree & Regresi Linear:")

    # Tombol preset pertanyaan cepat
    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        if st.button("💡 Cara kerja model?"):
            prompt_q = "Bagaimana cara kerja model Decision Tree dan Regresi di web ini?"
            st.session_state.chat_history.append({"role": "user", "content": prompt_q})
            with st.spinner("CineBot merespons..."):
                ctx = {"runtime": runtime, "votes": votes, "budget": budget, "year": year, "kualitas": pred_kualitas, "skor_imdb": pred_skor}
                reply = ask_cinebot(prompt_q, ctx)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    with col_q2:
        if st.button("📊 Mengapa vote dominan?"):
            prompt_q = "Mengapa jumlah vote lebih berpengaruh daripada anggaran?"
            st.session_state.chat_history.append({"role": "user", "content": prompt_q})
            with st.spinner("CineBot merespons..."):
                ctx = {"runtime": runtime, "votes": votes, "budget": budget, "year": year, "kualitas": pred_kualitas, "skor_imdb": pred_skor}
                reply = ask_cinebot(prompt_q, ctx)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    with col_q3:
        if st.button("🎬 Analisis parameter saat ini"):
            prompt_q = "cara mengatasi kalsifikasi kuliatas film yang 'kurang' atau analisis parameter saat ini"
            st.session_state.chat_history.append({"role": "user", "content": prompt_q})
            with st.spinner("CineBot merespons..."):
                ctx = {"runtime": runtime, "votes": votes, "budget": budget, "year": year, "kualitas": pred_kualitas, "skor_imdb": pred_skor}
                reply = ask_cinebot(prompt_q, ctx)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Inisialisasi riwayat chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Halo! Saya **CineBot**, asisten analitik CineMetrics. Silakan ajukan pertanyaan seputar model atau analisis film Anda."}
        ]

    # Render riwayat chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_query = st.chat_input("Tanyakan analisis film atau cara kerja model ke CineBot...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("CineBot sedang memproses..."):
                ctx = {"runtime": runtime, "votes": votes, "budget": budget, "year": year, "kualitas": pred_kualitas, "skor_imdb": pred_skor}
                bot_reply = ask_cinebot(user_query, ctx)
            st.markdown(bot_reply)
            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
