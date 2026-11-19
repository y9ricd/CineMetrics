import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "movies_clean.csv"

def train_and_export():
    print("=" * 60)
    print("PROSES PELATIHAN MODEL CINEMETRICS MACHINE LEARNING PIPELINE")
    print("=" * 60)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset tidak ditemukan di: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print(f"1. Membaca dataset: {df.shape[0]} baris, {df.shape[1]} kolom.")

    # Pembersihan data dan validasi kelengkapan fitur
    required_cols = ["runtime", "votes", "budget", "year", "score"]
    df_clean = df.dropna(subset=required_cols).copy()
    df_clean = df_clean[df_clean["budget"] > 0].reset_index(drop=True)
    print(f"2. Setelah pembersihan (budget > 0, dropna): {df_clean.shape[0]} baris.")

    # Diskretisasi target kualitas film sesuai standar industri
    # < 6.0: Kurang, 6.0 - < 7.0: Bagus, >= 7.0: Sangat Bagus
    df_clean["kualitas"] = pd.cut(
        df_clean["score"],
        bins=[0, 6.0, 7.0, 11.0],
        right=False,
        labels=["Kurang", "Bagus", "Sangat Bagus"]
    ).astype(str)

    features_clf = ["runtime", "votes", "budget", "year"]
    X_clf = df_clean[features_clf]
    y_clf = df_clean["kualitas"]

    # 1. Pelatihan Model Pohon Keputusan (Decision Tree Classifier)
    pohon_f = DecisionTreeClassifier(max_depth=3, random_state=42)
    pohon_f.fit(X_clf, y_clf)
    y_clf_pred = pohon_f.predict(X_clf)
    acc_clf = accuracy_score(y_clf, y_clf_pred)
    print(f"3. Model Decision Tree terlatih. Akurasi data latih: {acc_clf:.3f}")

    # 2. Pelatihan Model Regresi Linear (Estimasi Skor IMDb)
    features_reg = ["runtime", "votes"]
    X_reg = df_clean[features_reg]
    y_reg = df_clean["score"]

    m_reg = LinearRegression()
    m_reg.fit(X_reg, y_reg)
    y_reg_pred = m_reg.predict(X_reg)
    r2_reg = r2_score(y_reg, y_reg_pred)
    mae_reg = mean_absolute_error(y_reg, y_reg_pred)
    print(f"4. Model Linear Regression terlatih. R2: {r2_reg:.3f}, MAE: {mae_reg:.3f}")

    # Ekspor model terstandarisasi dengan joblib
    clf_path = BASE_DIR / "model_quality.joblib"
    reg_path = BASE_DIR / "model_score.joblib"
    joblib.dump(pohon_f, clf_path)
    joblib.dump(m_reg, reg_path)
    print(f"5. Model berhasil diekspor ke:\n   - {clf_path}\n   - {reg_path}")

    # Ekstraksi Feature Importances
    importances = dict(zip(features_clf, [round(float(v), 4) for v in pohon_f.feature_importances_]))
    classes = list(pohon_f.classes_)

    # Statistik Fitur untuk panduan form UI
    stats = {}
    for col in features_clf:
        stats[col] = {
            "min": float(df_clean[col].min()),
            "max": float(df_clean[col].max()),
            "median": float(df_clean[col].median()),
            "mean": round(float(df_clean[col].mean()), 2)
        }

    meta = {
        "dataset_name": "movies_clean.csv",
        "total_samples": int(len(df_clean)),
        "features_classification": features_clf,
        "features_regression": features_reg,
        "classes": classes,
        "decision_tree": {
            "max_depth": 3,
            "accuracy_train": round(float(acc_clf), 4),
            "feature_importances": importances
        },
        "linear_regression": {
            "r2_train": round(float(r2_reg), 4),
            "mae_train": round(float(mae_reg), 4),
            "intercept": round(float(m_reg.intercept_), 4),
            "coefficients": dict(zip(features_reg, [round(float(c), 6) for c in m_reg.coef_]))
        },
        "feature_stats": stats,
        "class_distribution": df_clean["kualitas"].value_counts().to_dict()
    }

    meta_path = BASE_DIR / "model_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"6. Metadata tersimpan di: {meta_path}")

    # Uji verifikasi mandiri (Self-verification)
    print("7. Menjalankan pengujian inferensi dummy:")
    test_sample = pd.DataFrame([{"runtime": 125, "votes": 200000, "budget": 50000000, "year": 2015}])
    pred_kualitas = pohon_f.predict(test_sample)[0]
    pred_skor = m_reg.predict(test_sample[features_reg])[0]
    print(f"   Sample Input: Runtime=125m, Votes=200k, Budget=$50M, Year=2015")
    print(f"   -> Prediksi Kualitas: '{pred_kualitas}'")
    print(f"   -> Estimasi Skor: {pred_skor:.2f} / 10.0")
    print("=" * 60)
    print("PIPELINE TRAINING DAN EKSPOR SELESAI DENGAN SUKSES!")
    print("=" * 60)

if __name__ == "__main__":
    train_and_export()
