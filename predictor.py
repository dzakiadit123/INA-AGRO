"""
predictor.py
Modul Inferensi AI & Explainability INA Agro (6 Komoditas Utama dari Kurasi Multi-Dataset Kaggle)
"""

import json
import os
from typing import Any, Dict, List
import joblib
import pandas as pd
from train_model import FEATURE_COLS, train_and_save

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "rf_ina_agro.joblib")
META_PATH = os.path.join(BASE_DIR, "artifacts", "model_metadata.json")

INA_AGRO_COMMODITY_NAMES: Dict[str, str] = {
    "shallot": "Bawang Merah",
    "garlic": "Bawang Putih",
    "red_chili": "Cabai Merah",
    "bird_eye_chili": "Cabai Rawit",
    "maize": "Jagung",
    "potato": "Kentang",
}

COMMODITY_KAGGLE_ORIGIN: Dict[str, str] = {
    "shallot": "srinivas1/allium-onion-garlic-yield-soil-dataset",
    "garlic": "srinivas1/allium-onion-garlic-yield-soil-dataset",
    "red_chili": "devendra111/capsicum-chili-cultivation-soil-climate",
    "bird_eye_chili": "devendra111/capsicum-chili-cultivation-soil-climate",
    "maize": "atharvaingle/crop-recommendation-dataset",
    "potato": "zsinghrahulk/potato-crop-dataset",
}

FACTOR_DISPLAY = {
    "N": ("Nitrogen (N)", "kg/ha"),
    "P": ("Fosfor (P)", "kg/ha"),
    "K": ("Kalium (K)", "kg/ha"),
    "temperature": ("Suhu", "°C"),
    "humidity": ("Kelembapan", "%"),
    "ph": ("pH tanah", "pH"),
    "rainfall": ("Curah hujan", "mm/bln"),
}


class InaAgroPredictor:
    def __init__(self):
        if not os.path.exists(MODEL_PATH) or not os.path.exists(META_PATH):
            train_and_save(output_dir=os.path.join(BASE_DIR, "artifacts"))
        self.model = joblib.load(MODEL_PATH)
        with open(META_PATH, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    @staticmethod
    def _classify_confidence_label(score_pct: float) -> str:
        if score_pct >= 55.0:
            return "Tinggi"
        if score_pct >= 25.0:
            return "Sedang"
        return "Rendah"

    @staticmethod
    def _map_suitability_class(score_pct: float, has_anomaly: bool) -> Dict[str, str]:
        if has_anomaly and score_pct < 25.0:
            return {
                "kode": "BL",
                "nama": "Kelas BL - Belum Dinilai",
                "deskripsi": "Parameter iklim atau hara berada di luar sebaran normal kurasi dataset Kaggle; perlu verifikasi lapangan.",
            }
        if score_pct >= 65.0:
            return {
                "kode": "S1",
                "nama": "Kelas S1 - Sangat Sesuai",
                "deskripsi": "Kondisi unsur hara tanah dan agroklimat sangat mendukung pertumbuhan optimal.",
            }
        if score_pct >= 35.0:
            return {
                "kode": "S2",
                "nama": "Kelas S2 - Cukup Sesuai",
                "deskripsi": "Lahan mempunyai pembatas ringan yang dapat diatasi dengan pemupukan berimbang.",
            }
        if score_pct >= 15.0:
            return {
                "kode": "S3",
                "nama": "Kelas S3 - Sesuai Marginal",
                "deskripsi": "Membutuhkan perbaikan kesuburan tanah dan pengaturan irigasi tambahan.",
            }
        return {
            "kode": "N",
            "nama": "Kelas N - Tidak Sesuai",
            "deskripsi": "Kondisi hara dan iklim kurang mendukung komoditas ini.",
        }

    @staticmethod
    def detect_anomalies(payload: Dict[str, Any]) -> List[Dict[str, str]]:
        anomalies = []
        if float(payload["rainfall"]) > 260:
            anomalies.append({
                "parameter": "Curah Hujan Tinggi",
                "pesan": f"Curah hujan {payload['rainfall']} mm/bulan berisiko memicu busuk umbi/akar pada hortikultura; pastikan bedengan berdrainase baik.",
            })
        elif float(payload["rainfall"]) < 35:
            anomalies.append({
                "parameter": "Curah Hujan Sangat Rendah",
                "pesan": f"Curah hujan {payload['rainfall']} mm/bulan memerlukan dukungan irigasi tambahan.",
            })

        if float(payload["temperature"]) > 35.0 or float(payload["temperature"]) < 12.0:
            anomalies.append({
                "parameter": "Suhu Ekstrem",
                "pesan": f"Suhu {payload['temperature']} °C berada di tepi sebaran iklim budidaya komoditas INA Agro.",
            })

        if float(payload["ph"]) < 4.8 or float(payload["ph"]) > 7.8:
            anomalies.append({
                "parameter": "pH Tanah Ekstrem",
                "pesan": f"pH tanah {payload['ph']} berada di luar rentang ideal (5.3–7.2); pertimbangkan pengapuran dolomit.",
            })
        return anomalies

    def build_factor_explanations(self, payload: Dict[str, Any], top_raw_label: str) -> List[Dict[str, str]]:
        crop_ranges = self.metadata.get("crop_ranges", {}).get(top_raw_label, {})
        explanations = []
        for col in FEATURE_COLS:
            label_id, unit = FACTOR_DISPLAY[col]
            val = float(payload[col])
            bounds = crop_ranges.get(col, [0, 999])
            low, high = float(bounds[0]), float(bounds[1])
            span = max(1.0, high - low)

            if low <= val <= high:
                status = "Sesuai"
            elif (low - span * 0.35) <= val <= (high + span * 0.35):
                status = "Cukup Sesuai"
            else:
                status = "Kurang Sesuai"

            explanations.append({
                "faktor": label_id,
                "nilai": f"{val:g} {unit}" if unit != "pH" else f"{val:g}",
                "status": status,
                "ideal": f"Train P10–P90: {low:g}–{high:g}",
            })
        return explanations

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row = {col: float(payload[col]) for col in FEATURE_COLS}
        input_df = pd.DataFrame([row])

        probas = self.model.predict_proba(input_df)[0]
        classes = self.model.classes_

        ranked = sorted(
            zip(classes, probas),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        anomalies = self.detect_anomalies(payload)
        has_anomaly = len(anomalies) > 0

        rekomendasi_top3 = []
        for raw_label, prob in ranked[:3]:
            raw_str = str(raw_label)
            skor_pct = round(float(prob) * 100, 1)
            kelas = self._map_suitability_class(skor_pct, has_anomaly)
            rekomendasi_top3.append({
                "komoditas": INA_AGRO_COMMODITY_NAMES.get(raw_str, raw_str),
                "label_dataset": raw_str,
                "sumber_kaggle": COMMODITY_KAGGLE_ORIGIN.get(raw_str, "Kaggle Curated"),
                "skor_kecocokan": skor_pct,
                "label": self._classify_confidence_label(skor_pct),
                "kelas_kesesuaian": kelas["nama"],
                "kode_kelas": kelas["kode"],
                "deskripsi_kelas": kelas["deskripsi"],
            })

        top_raw = rekomendasi_top3[0]["label_dataset"]
        faktor_penjelas = self.build_factor_explanations(payload, top_raw)

        return {
            "status": "success",
            "curation_strategy": self.metadata.get("curation_strategy"),
            "evaluation_splits": self.metadata.get("data_splits"),
            "lokasi_wilayah": payload.get("lokasi_wilayah", "Kec. Dramaga, Kab. Bogor"),
            "rekomendasi_top3": rekomendasi_top3,
            "faktor_penjelas": faktor_penjelas,
            "anomali_cuaca": anomalies,
            "feature_importance_global": self.metadata.get("feature_importance_global", {}),
            "catatan": (
                "Hasil merupakan estimasi model Random Forest dari kurasi 4 dataset Kaggle untuk 6 komoditas utama INA Agro "
                "(70% Train, 15% Validation, 15% Test), bukan jaminan hasil panen."
            ),
        }
