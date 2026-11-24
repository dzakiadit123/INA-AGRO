@echo off
echo Menjalankan server INA Agro (Opsi B: Kurasi Multi-Dataset Kaggle) di http://127.0.0.1:8000 ...
python -m uvicorn app:app --reload
pause
