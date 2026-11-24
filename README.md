# INA Agro — Kurasi Multi-Dataset Kaggle (Opsi B) untuk 6 Komoditas Utama

## Strategi Kurasi Multi-Dataset Kaggle (`train_model.py`)
Untuk mempertahankan **6 Komoditas Utama INA Agro** (*Bawang Merah, Bawang Putih, Cabai Merah, Cabai Rawit, Jagung, Kentang*), skrip `train_model.py` melakukan harmonisasi skema dari **4 dataset Kaggle** di dalam `data/raw_kaggle/`:

1. **`atharvaingle/crop-recommendation-dataset`** (`kaggle_crop_recommendation.csv`) → mengambil kelas `maize` (**Jagung**).
2. **`zsinghrahulk/potato-crop-dataset`** (`kaggle_potato_agronomy.csv`) → mengambil kelas `potato` (**Kentang**).
3. **`srinivas1/allium-onion-garlic-yield-soil-dataset`** (`kaggle_allium_horticulture.csv`) → mengambil kelas `shallot` (**Bawang Merah**) & `garlic` (**Bawang Putih**).
4. **`devendra111/capsicum-chili-cultivation-soil-climate`** (`kaggle_capsicum_chili.csv`) → mengambil kelas `red_chili` (**Cabai Merah**) & `bird_eye_chili` (**Cabai Rawit**).

Hasil kurasi disimpan ke `data/ina_agro_kaggle_curated.csv` (1.800 sampel = 6 komoditas × 300 sampel), lalu dibagi menggunakan *Stratified Split*:
* **Training Set (70% — 1.260 sampel)**: `data/splits/train.csv`
* **Validation Set (15% — 270 sampel)**: `data/splits/validation.csv`
* **Testing Set (15% — 270 sampel)**: `data/splits/test.csv`

## Cara Menjalankan di VS Code
1. Buka folder `ina-agro` di VS Code.
2. Instal dependensi (jika belum):
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Jalankan pipeline kurasi, training, validation, dan testing:
   ```powershell
   python train_model.py
   ```
4. Jalankan server FastAPI:
   ```powershell
   python -m uvicorn app:app --reload
   ```
5. Buka **`http://127.0.0.1:8000`** di browser.
