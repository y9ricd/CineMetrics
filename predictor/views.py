import json
import logging
from datetime import timedelta
from pathlib import Path
from django.conf import settings
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
import joblib
import numpy as np
import pandas as pd
from .forms import MoviePredictionForm
from .ai_service import generate_movie_insight, ask_cinebot
from .models import PredictionHistory

logger = logging.getLogger(__name__)

ML_DIR = settings.BASE_DIR / "ml_model"
_MODEL_CACHE = {}

def get_ml_assets():
    """Memuat model biner dan metadata dengan caching di memori."""
    if not _MODEL_CACHE:
        clf_path = ML_DIR / "model_quality.joblib"
        reg_path = ML_DIR / "model_score.joblib"
        meta_path = ML_DIR / "model_meta.json"

        if not clf_path.exists() or not reg_path.exists():
            raise FileNotFoundError(
                f"Model file tidak ditemukan di {ML_DIR}. "
                "Harap jalankan 'python ml_model/train_and_export.py' terlebih dahulu."
            )

        _MODEL_CACHE["clf"] = joblib.load(clf_path)
        _MODEL_CACHE["reg"] = joblib.load(reg_path)

        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                _MODEL_CACHE["meta"] = json.load(f)
        else:
            _MODEL_CACHE["meta"] = {}

    return _MODEL_CACHE["clf"], _MODEL_CACHE["reg"], _MODEL_CACHE["meta"]

def get_chart_data():
    """Mengagregasi data dari dataset movies_clean.csv untuk grafik visualisasi."""
    if "chart_data" in _MODEL_CACHE:
        return _MODEL_CACHE["chart_data"]

    csv_path = ML_DIR / "movies_clean.csv"
    if not csv_path.exists():
        chart_data = {
            "kualitas_labels": ["Kurang (<6.0)", "Bagus (6-7)", "Sangat Bagus (≥7.0)"],
            "kualitas_counts": [1562, 2291, 1568],
            "kualitas_scores": [5.23, 6.45, 7.46],
            "genre_labels": ["Biography", "Drama", "Animation", "Crime", "Adventure", "Action", "Comedy"],
            "genre_scores": [7.09, 6.72, 6.69, 6.69, 6.27, 6.25, 6.19],
            "importance_labels": ["Resonansi Votes", "Durasi Tayang", "Anggaran (USD)", "Tahun Rilis"],
            "importance_values": [68.3, 19.0, 12.7, 0.0]
        }
    else:
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

            # 1. Agregasi per kualitas
            q_agg = df.groupby("kualitas")["score"].agg(["count", "mean"]).reindex(["Kurang", "Bagus", "Sangat Bagus"])
            kualitas_labels = ["Kurang (<6.0)", "Bagus (6-7)", "Sangat Bagus (≥7.0)"]
            kualitas_counts = [int(c) for c in q_agg["count"]]
            kualitas_scores = [round(float(s), 2) for s in q_agg["mean"]]

            # 2. Agregasi top 7 genre
            top_g = df["genre"].value_counts().head(7).index
            g_agg = df[df["genre"].isin(top_g)].groupby("genre")["score"].mean().sort_values(ascending=False)
            genre_labels = list(g_agg.index)
            genre_scores = [round(float(s), 2) for s in g_agg.values]

            # 3. Feature importance
            _, _, meta = get_ml_assets()
            fi = meta.get("decision_tree", {}).get("feature_importances", {})
            importance_labels = ["Resonansi Votes", "Durasi Tayang", "Anggaran (USD)", "Tahun Rilis"]
            importance_values = [
                round(float(fi.get("votes", 0.6827)) * 100, 1),
                round(float(fi.get("runtime", 0.1903)) * 100, 1),
                round(float(fi.get("budget", 0.1270)) * 100, 1),
                round(float(fi.get("year", 0.0)) * 100, 1)
            ]

            chart_data = {
                "kualitas_labels": kualitas_labels,
                "kualitas_counts": kualitas_counts,
                "kualitas_scores": kualitas_scores,
                "genre_labels": genre_labels,
                "genre_scores": genre_scores,
                "importance_labels": importance_labels,
                "importance_values": importance_values
            }
        except Exception as e:
            logger.warning("Gagal mengolah dataset movies_clean.csv untuk grafik: %s", e)
            chart_data = {
                "kualitas_labels": ["Kurang (<6.0)", "Bagus (6-7)", "Sangat Bagus (≥7.0)"],
                "kualitas_counts": [1562, 2291, 1568],
                "kualitas_scores": [5.23, 6.45, 7.46],
                "genre_labels": ["Biography", "Drama", "Animation", "Crime", "Adventure", "Action", "Comedy"],
                "genre_scores": [7.09, 6.72, 6.69, 6.69, 6.27, 6.25, 6.19],
                "importance_labels": ["Resonansi Votes", "Durasi Tayang", "Anggaran (USD)", "Tahun Rilis"],
                "importance_values": [68.3, 19.0, 12.7, 0.0]
            }

    _MODEL_CACHE["chart_data"] = chart_data
    return chart_data

def index_view(request):
    clf, reg, meta = get_ml_assets()
    result = None

    if request.method == "POST":
        form = MoviePredictionForm(request.POST)
        if form.is_valid():
            runtime = form.cleaned_data["runtime"]
            votes = form.cleaned_data["votes"]
            budget = form.cleaned_data["budget"]
            year = form.cleaned_data["year"]

            # Feature Vector Alignment: Susun DataFrame dengan kolom & tipe data identik saat training
            # 1. Inferensi Klasifikasi Kualitas (Decision Tree)
            df_clf = pd.DataFrame([{
                "runtime": runtime,
                "votes": votes,
                "budget": budget,
                "year": year
            }])
            pred_kualitas = clf.predict(df_clf)[0]

            # Probabilitas kelas (Decision Tree)
            class_probs = {}
            if hasattr(clf, "predict_proba"):
                probs = clf.predict_proba(df_clf)[0]
                for cls_name, prob in zip(clf.classes_, probs):
                    class_probs[cls_name] = round(float(prob) * 100, 1)

            # 2. Inferensi Regresi Skor IMDb (Linear Regression)
            df_reg = pd.DataFrame([{
                "runtime": runtime,
                "votes": votes
            }])
            pred_skor = float(reg.predict(df_reg)[0])
            # Batasi skor pada skala logis IMDb (1.0 - 10.0)
            pred_skor_clamped = max(1.0, min(10.0, round(pred_skor, 2)))

            # Warna badge & ikon status
            if pred_kualitas == "Sangat Bagus":
                badge_class = "success"
                status_icon = "bi-stars"
            elif pred_kualitas == "Bagus":
                badge_class = "primary"
                status_icon = "bi-hand-thumbs-up-fill"
            else:
                badge_class = "warning"
                status_icon = "bi-exclamation-triangle-fill"

            # Analisis AI Dinamis (Gemini Generative AI / Smart Engine)
            insight = generate_movie_insight(
                runtime=runtime,
                votes=votes,
                budget=budget,
                year=year,
                kualitas=pred_kualitas,
                skor_imdb=pred_skor_clamped
            )

            result = {
                "kualitas": pred_kualitas,
                "skor_imdb": pred_skor_clamped,
                "skor_persen": round((pred_skor_clamped / 10.0) * 100, 1),
                "badge_class": badge_class,
                "status_icon": status_icon,
                "insight": insight,
                "class_probs": class_probs,
                "input_data": {
                    "runtime": runtime,
                    "votes": f"{votes:,}",
                    "budget": f"${budget:,.0f}",
                    "year": year
                }
            }

            # Simpan riwayat prediksi ke SQLite (PredictionHistory)
            # Filter duplikasi akibat double-click atau request paralel
            market_score = int(round(pred_skor_clamped * 10))
            try:
                recent_window = timezone.now() - timedelta(seconds=5)
                is_duplicate = (
                    PredictionHistory.objects.filter(
                        runtime=runtime,
                        votes=votes,
                        year=year,
                        created_at__gte=recent_window
                    ).filter(
                        budget__gte=budget - 1.0,
                        budget__lte=budget + 1.0
                    ).exists()
                )
                if not is_duplicate:
                    latest = PredictionHistory.objects.order_by("-id").first()
                    if not (
                        latest is not None
                        and latest.runtime == runtime
                        and latest.votes == votes
                        and abs(latest.budget - budget) < 1.0
                        and latest.year == year
                    ):
                        PredictionHistory.objects.create(
                            runtime=runtime,
                            votes=votes,
                            budget=budget,
                            year=year,
                            kualitas=pred_kualitas,
                            skor_imdb=pred_skor_clamped,
                            prob_kurang=class_probs.get("Kurang", 0.0),
                            prob_bagus=class_probs.get("Bagus", 0.0),
                            prob_sangat_bagus=class_probs.get("Sangat Bagus", 0.0),
                            market_score=market_score,
                            insight=insight
                        )
            except Exception as e:
                logger.exception("Gagal menyimpan riwayat prediksi ke database: %s", e)

            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1":
                return JsonResponse({"success": True, "result": result})
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1":
                return JsonResponse({"success": False, "errors": form.errors.get_json_data()}, status=400)
    else:
        # Nilai default awal saat GET
        form = MoviePredictionForm()

    chart_data = get_chart_data()
    recent_history = PredictionHistory.objects.all()[:50]
    total_history_count = PredictionHistory.objects.count()

    avg_score = 6.4
    if total_history_count > 0:
        avg_res = PredictionHistory.objects.aggregate(Avg("skor_imdb"))
        if avg_res.get("skor_imdb__avg"):
            avg_score = round(float(avg_res["skor_imdb__avg"]), 1)

    context = {
        "form": form,
        "result": result,
        "meta": meta,
        "chart_data": chart_data,
        "chart_data_json": json.dumps(chart_data),
        "importances": meta.get("decision_tree", {}).get("feature_importances", {}),
        "total_samples": meta.get("total_samples", 5421),
        "recent_history": recent_history,
        "total_history_count": total_history_count,
        "avg_score": avg_score,
    }

    return render(request, "predictor/index.html", context)


def chat_view(request):
    """Endpoint API ChatBot untuk asisten CineBot."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Hanya menerima metode POST"}, status=405)

    try:
        # Dukung pembacaan payload JSON atau POST form-data
        if request.content_type == "application/json":
            payload = json.loads(request.body.decode("utf-8"))
        else:
            payload = request.POST

        message = payload.get("message", "").strip()
        if not message:
            return JsonResponse({"success": False, "error": "Pesan tidak boleh kosong"}, status=400)

        context = {
            "runtime": int(payload.get("runtime", 120)),
            "votes": int(payload.get("votes", 150000)),
            "budget": float(payload.get("budget", 35000000)),
            "year": int(payload.get("year", 2021)),
            "kualitas": payload.get("kualitas", ""),
            "skor_imdb": payload.get("skor_imdb", "")
        }

        reply = ask_cinebot(message, current_context=context)
        return JsonResponse({"success": True, "reply": reply})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def history_api_view(request):
    """Endpoint API untuk mengambil atau membersihkan riwayat prediksi terbaru."""
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "clear":
            PredictionHistory.objects.all().delete()
            return JsonResponse({
                "success": True,
                "message": "Riwayat prediksi berhasil dibersihkan.",
                "count": 0,
                "total_count": 0,
                "history": []
            })

    limit = int(request.GET.get("limit", 50))
    limit = max(1, min(100, limit))
    history_qs = PredictionHistory.objects.all()[:limit]
    data = []
    for h in history_qs:
        data.append({
            "id": h.id,
            "created_at": h.created_at.strftime("%d %b %Y, %H:%M"),
            "created_at_raw": h.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "runtime": h.runtime,
            "votes": h.votes,
            "budget": h.budget,
            "year": h.year,
            "kualitas": h.kualitas,
            "skor_imdb": h.skor_imdb,
            "prob_kurang": h.prob_kurang,
            "prob_bagus": h.prob_bagus,
            "prob_sangat_bagus": h.prob_sangat_bagus,
            "market_score": h.market_score,
            "insight": h.insight or "",
        })
    total_count = PredictionHistory.objects.count()
    return JsonResponse({"success": True, "count": len(data), "total_count": total_count, "history": data})

