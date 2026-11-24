import os
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from predictor import InaAgroPredictor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="INA Agro — Sistem Evaluasi Kesesuaian Lahan AI",
    description="Rekomendasi 6 Komoditas Utama INA Agro Berbasis Kurasi Multi-Dataset Kaggle",
    version="4.0.0",
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

predictor = InaAgroPredictor()


class LandConditionInput(BaseModel):
    N: float = Field(..., ge=0.0, le=200.0, description="Rasio kandungan Nitrogen (kg/ha)")
    P: float = Field(..., ge=0.0, le=200.0, description="Rasio kandungan Fosfor (kg/ha)")
    K: float = Field(..., ge=0.0, le=250.0, description="Rasio kandungan Kalium (kg/ha)")
    temperature: float = Field(..., ge=5.0, le=45.0, description="Suhu rata-rata (°C)")
    humidity: float = Field(..., ge=10.0, le=100.0, description="Kelembapan udara relatif (%)")
    ph: float = Field(..., ge=3.5, le=9.9, description="Tingkat keasaman tanah (pH)")
    rainfall: float = Field(..., ge=0.0, le=500.0, description="Curah hujan bulanan (mm/bulan)")
    lokasi_wilayah: Optional[str] = Field(
        default="Kec. Dramaga, Kab. Bogor",
        description="Lokasi tingkat kecamatan/wilayah agroekologi",
    )
    consent_opt_in: Optional[bool] = Field(default=False)


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": "INA Agro",
            "meta": predictor.metadata,
        },
    )


@app.get("/api/metrics")
async def model_metrics():
    return {
        "curation_strategy": predictor.metadata.get("curation_strategy"),
        "kaggle_sources": predictor.metadata.get("kaggle_sources"),
        "data_splits": predictor.metadata.get("data_splits"),
        "selected_hyperparameters": predictor.metadata.get("selected_hyperparameters"),
        "feature_importance_global": predictor.metadata.get("feature_importance_global"),
    }


@app.post("/api/predict")
async def predict_commodity(data: LandConditionInput):
    return predictor.predict(data.model_dump())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
