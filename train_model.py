"""
train_model.py
Pipeline Kurasi Multi-Dataset Kaggle (Opsi B) untuk 6 Komoditas Utama INA Agro (Kelompok 15)

Sumber Kurasi Multi-Dataset Kaggle (data/raw_kaggle/):
1. atharvaingle/crop-recommendation-dataset      -> Kelas `maize` (Jagung)
2. zsinghrahulk/potato-crop-dataset              -> Kelas `potato` (Kentang)
3. srinivas1/allium-onion-garlic-yield-soil      -> Kelas `shallot` (Bawang Merah) & `garlic` (Bawang Putih)
4. devendra111/capsicum-chili-cultivation-soil   -> Kelas `red_chili` (Cabai Merah) & `bird_eye_chili` (Cabai Rawit)

Output Kurasi Terpadu:
- Dataset Terpadu : data/ina_agro_kaggle_curated.csv (1.800 sampel = 6 komoditas x 300 sampel)
- Training Set    : data/splits/train.csv (70% = 1.260 sampel)
- Validation Set  : data/splits/validation.csv (15% = 270 sampel)
- Testing Set     : data/splits/test.csv (15% = 270 sampel)
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_KAGGLE_DIR = os.path.join(BASE_DIR, "data", "raw_kaggle")
SPLITS_DIR = os.path.join(BASE_DIR, "data", "splits")
CURATED_DATA_PATH = os.path.join(BASE_DIR, "data", "ina_agro_kaggle_curated.csv")

FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COMMODITIES = [
    "shallot",         # Bawang Merah
    "garlic",          # Bawang Putih
    "red_chili",       # Cabai Merah
    "bird_eye_chili",  # Cabai Rawit
    "maize",           # Jagung
    "potato",          # Kentang
]

KAGGLE_CURATION_SOURCES = [
    {
        "dataset_title": "Crop Recommendation Dataset (Atharva Ingle)",
        "kaggle_slug": "atharvaingle/crop-recommendation-dataset",
        "kaggle_url": "https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset",
        "raw_file": "data/raw_kaggle/kaggle_crop_recommendation.csv",
        "extracted_classes": ["maize (Jagung)"],
    },
    {
        "dataset_title": "Potato Crop Agronomy & Soil Dataset",
        "kaggle_slug": "zsinghrahulk/potato-crop-dataset",
        "kaggle_url": "https://www.kaggle.com/datasets/zsinghrahulk/potato-crop-dataset",
        "raw_file": "data/raw_kaggle/kaggle_potato_agronomy.csv",
        "extracted_classes": ["potato (Kentang)"],
    },
    {
        "dataset_title": "Allium (Onion & Garlic) Soil-Climate Dataset",
        "kaggle_slug": "srinivas1/allium-onion-garlic-yield-soil-dataset",
        "kaggle_url": "https://www.kaggle.com/datasets/srinivas1/allium-onion-garlic-yield-soil-dataset",
        "raw_file": "data/raw_kaggle/kaggle_allium_horticulture.csv",
        "extracted_classes": ["shallot (Bawang Merah)", "garlic (Bawang Putih)"],
    },
    {
        "dataset_title": "Capsicum & Chili Cultivation Soil-Climate Dataset",
        "kaggle_slug": "devendra111/capsicum-chili-cultivation-soil-climate",
        "kaggle_url": "https://www.kaggle.com/datasets/devendra111/capsicum-chili-cultivation-soil-climate",
        "raw_file": "data/raw_kaggle/kaggle_capsicum_chili.csv",
        "extracted_classes": ["red_chili (Cabai Merah)", "bird_eye_chili (Cabai Rawit)"],
    },
]


def curate_multi_kaggle_datasets() -> pd.DataFrame:
    """Harmonisasi skema 4 sumber Kaggle menjadi 1 dataset terpadu 6 komoditas utama INA Agro."""
    frames = []

    # 1. Sumber Kaggle Crop Recommendation -> filter hanya 'maize'
    p1 = os.path.join(RAW_KAGGLE_DIR, "kaggle_crop_recommendation.csv")
    if os.path.exists(p1):
        df1 = pd.read_csv(p1)
        df1 = df1[df1["label"].isin(["maize"])].copy()
        df1["source_kaggle"] = "atharvaingle/crop-recommendation-dataset"
        frames.append(df1[FEATURE_COLS + ["label", "source_kaggle"]])

    # 2. Sumber Kaggle Potato Agronomy -> normalisasi nama kolom
    p2 = os.path.join(RAW_KAGGLE_DIR, "kaggle_potato_agronomy.csv")
    if os.path.exists(p2):
        df2 = pd.read_csv(p2).rename(columns={
            "Nitrogen": "N",
            "Phosphorus": "P",
            "Potassium": "K",
            "Temp_C": "temperature",
            "Humidity_Pct": "humidity",
            "Soil_pH": "ph",
            "Rainfall_mm": "rainfall",
            "Crop": "label",
        })
        df2["source_kaggle"] = "zsinghrahulk/potato-crop-dataset"
        frames.append(df2[FEATURE_COLS + ["label", "source_kaggle"]])

    # 3. Sumber Kaggle Allium (Shallot & Garlic) -> normalisasi nama kolom
    p3 = os.path.join(RAW_KAGGLE_DIR, "kaggle_allium_horticulture.csv")
    if os.path.exists(p3):
        df3 = pd.read_csv(p3).rename(columns={
            "N_kg_ha": "N",
            "P_kg_ha": "P",
            "K_kg_ha": "K",
            "Temperature": "temperature",
            "Humidity": "humidity",
            "pH": "ph",
            "Rainfall": "rainfall",
            "Commodity": "label",
        })
        df3["source_kaggle"] = "srinivas1/allium-onion-garlic-yield-soil-dataset"
        frames.append(df3[FEATURE_COLS + ["label", "source_kaggle"]])

    # 4. Sumber Kaggle Capsicum & Chili (Red Chili & Bird's Eye Chili)
    p4 = os.path.join(RAW_KAGGLE_DIR, "kaggle_capsicum_chili.csv")
    if os.path.exists(p4):
        df4 = pd.read_csv(p4)
        df4["source_kaggle"] = "devendra111/capsicum-chili-cultivation-soil-climate"
        frames.append(df4[FEATURE_COLS + ["label", "source_kaggle"]])

    if frames:
        curated_df = pd.concat(frames, ignore_index=True)
        curated_df = curated_df[curated_df["label"].isin(TARGET_COMMODITIES)].dropna().reset_index(drop=True)
        curated_df.to_csv(CURATED_DATA_PATH, index=False)
        return curated_df

    if os.path.exists(CURATED_DATA_PATH):
        return pd.read_csv(CURATED_DATA_PATH)

    raise FileNotFoundError("Berkas dataset Kaggle di data/raw_kaggle/ tidak ditemukan.")


def compute_top_k_accuracy(y_true: np.ndarray, y_proba: np.ndarray, classes: np.ndarray, k: int = 3) -> float:
    top_k_idx = np.argsort(y_proba, axis=1)[:, -k:]
    top_k_labels = classes[top_k_idx]
    hits = [y_true[i] in top_k_labels[i] for i in range(len(y_true))]
    return float(np.mean(hits))


def evaluate_split(model: RandomForestClassifier, X_split: pd.DataFrame, y_split: np.ndarray) -> dict:
    y_pred = model.predict(X_split)
    y_proba = model.predict_proba(X_split)
    classes = model.classes_

    return {
        "samples": int(len(y_split)),
        "top1_accuracy": round(float(accuracy_score(y_split, y_pred)) * 100, 2),
        "top3_accuracy": round(compute_top_k_accuracy(y_split, y_proba, classes, k=3) * 100, 2),
        "macro_precision": round(float(precision_score(y_split, y_pred, average="macro", zero_division=0)) * 100, 2),
        "macro_recall": round(float(recall_score(y_split, y_pred, average="macro", zero_division=0)) * 100, 2),
        "macro_f1": round(float(f1_score(y_split, y_pred, average="macro", zero_division=0)) * 100, 2),
    }


def train_and_save(output_dir: str = None):
    if output_dir is None:
        output_dir = os.path.join(BASE_DIR, "artifacts")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(SPLITS_DIR, exist_ok=True)

    # 1. Kurasi 4 sumber Kaggle menjadi 1 dataset utama (6 komoditas INA Agro)
    df = curate_multi_kaggle_datasets()

    # 2. Stratified Split: 70% Training, 15% Validation, 15% Testing
    train_df, temp_df = train_test_split(
        df, test_size=0.30, random_state=42, stratify=df["label"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=42, stratify=temp_df["label"]
    )

    train_df.to_csv(os.path.join(SPLITS_DIR, "train.csv"), index=False)
    val_df.to_csv(os.path.join(SPLITS_DIR, "validation.csv"), index=False)
    test_df.to_csv(os.path.join(SPLITS_DIR, "test.csv"), index=False)

    X_train, y_train = train_df[FEATURE_COLS], train_df["label"].values
    X_val, y_val = val_df[FEATURE_COLS], val_df["label"].values
    X_test, y_test = test_df[FEATURE_COLS], test_df["label"].values

    # 3. Seleksi Hyperparameter menggunakan Validation Set
    candidate_configs = [
        {"n_estimators": 100, "max_depth": 10, "min_samples_leaf": 2},
        {"n_estimators": 200, "max_depth": 14, "min_samples_leaf": 1},
        {"n_estimators": 300, "max_depth": None, "min_samples_leaf": 1},
    ]

    best_model = None
    best_cfg = None
    best_val_acc = -1.0
    validation_trials = []

    for cfg in candidate_configs:
        clf = RandomForestClassifier(
            n_estimators=cfg["n_estimators"],
            max_depth=cfg["max_depth"],
            min_samples_leaf=cfg["min_samples_leaf"],
            random_state=42,
            n_jobs=-1,
        )
        clf.fit(X_train, y_train)
        val_acc = float(accuracy_score(y_val, clf.predict(X_val)))
        validation_trials.append({
            "params": cfg,
            "val_accuracy_pct": round(val_acc * 100, 2),
        })
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model = clf
            best_cfg = cfg

    # 4. Evaluasi pada Training, Validation, dan Testing Set
    train_metrics = evaluate_split(best_model, X_train, y_train)
    val_metrics = evaluate_split(best_model, X_val, y_val)
    test_metrics = evaluate_split(best_model, X_test, y_test)

    feature_importance = {
        feat: round(float(imp), 4)
        for feat, imp in sorted(
            zip(FEATURE_COLS, best_model.feature_importances_),
            key=lambda x: x[1],
            reverse=True,
        )
    }

    # Kuantil P10–P90 dari Training Set (bebas data leakage)
    crop_ranges = {}
    for label, group in train_df.groupby("label"):
        crop_ranges[str(label)] = {
            col: [round(float(group[col].quantile(0.10)), 1), round(float(group[col].quantile(0.90)), 1)]
            for col in FEATURE_COLS
        }

    model_path = os.path.join(output_dir, "rf_ina_agro.joblib")
    meta_path = os.path.join(output_dir, "model_metadata.json")

    joblib.dump(best_model, model_path)

    metadata = {
        "curation_strategy": "Opsi B — Kurasi Multi-Dataset Kaggle untuk 6 Komoditas Utama INA Agro",
        "kaggle_sources": KAGGLE_CURATION_SOURCES,
        "curated_dataset": {
            "file": "data/ina_agro_kaggle_curated.csv",
            "total_rows": int(len(df)),
            "num_classes": int(df["label"].nunique()),
            "classes": TARGET_COMMODITIES,
        },
        "data_splits": {
            "strategy": "Stratified Split 70% Train / 15% Validation / 15% Test",
            "train": train_metrics,
            "validation": val_metrics,
            "test": test_metrics,
        },
        "selected_hyperparameters": best_cfg,
        "validation_trials": validation_trials,
        "algorithm": "RandomForestClassifier (Scikit-learn)",
        "features": FEATURE_COLS,
        "feature_importance_global": feature_importance,
        "crop_ranges": crop_ranges,
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("=== PIPELINE KURASI MULTI-DATASET KAGGLE (6 KOMODITAS INA AGRO) ===")
    print(f"Dataset Terpadu : data/ina_agro_kaggle_curated.csv ({len(df)} baris, {df['label'].nunique()} komoditas)")
    print(f"Split Dataset   : Train={train_metrics['samples']} | Val={val_metrics['samples']} | Test={test_metrics['samples']}")
    print(f"Validation Acc  : Top-1 = {val_metrics['top1_accuracy']}% | Top-3 = {val_metrics['top3_accuracy']}%")
    print(f"Testing Acc     : Top-1 = {test_metrics['top1_accuracy']}% | Top-3 = {test_metrics['top3_accuracy']}% | F1 = {test_metrics['macro_f1']}%")


if __name__ == "__main__":
    train_and_save()
