# ZooLens

Aplikasi web edukasi satwa: Laravel Blade + FastAPI + YOLO11n.

## Struktur
- `backend/`: Laravel web app (dibuat melalui script bootstrap)
- `ai-service/`: FastAPI inference service
- `ml/`: training config/scripts
- `docs/`: dokumentasi arsitektur dan pembagian kerja

## Prasyarat Windows
PHP 8.2+, Composer, Node.js LTS + npm, Python 3.11, Git. Untuk Laravel gunakan PHP/Composer yang kompatibel dengan versi Laravel yang terpasang.

## Mulai
Dari root repository di PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/init-laravel.ps1
powershell -ExecutionPolicy Bypass -File scripts/setup-ai.ps1
```

Terminal 1:
```powershell
cd backend
composer run dev
```

Terminal 2:
```powershell
cd ai-service
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

FastAPI docs: http://127.0.0.1:8001/docs ; health: http://127.0.0.1:8001/health

## Status Milestone 1 (W1–W5 — UTS 2 November 2026)
- **AI Microservice (`ai-service/`):** FastAPI di port 8001 aktif melayani inferensi real-time via `/predict` menggunakan bobot YOLO11n (`best.pt`). Dilengkapi unit tests (pytest lulus).
- **Web Backend & UI (`backend/`):** Laravel 11 + Blade + Tailwind CDN di port 8000:
  - Smart Animal Scanner (kamera langsung & unggah galeri) dengan overlay bounding box dinamis.
  - Interactive Animal Factsheet untuk 5 satwa (*elephant, giraffe, zebra, tiger, rhinoceros*).
  - Tampilan Zoo Digital Safari & Riwayat Deteksi.
  - Skema database 4 tabel (`animals`, `badges`, `user_animals`, `detections`) dengan SQLite memory testing (11 tests lulus).
- **Evaluasi & Pengujian ML (`ml/`):**
  - Runner batch testing otomatis 200 citra (`ml/scripts/batch_test_200.py`).
  - Hasil evaluasi oklusi dan pemotongan (truncation) tersimpan di `ml/test_results_200/`.
  - Hipotesis pengujian dan kerangka analisis di `docs/HIPOTESIS_PENGUJIAN_200.md` dan `docs/LAPORAN_MILESTONE_1.md`.

## Git
```powershell
git init
git branch -M main
git add .
git commit -m "chore: scaffold ZooLens monorepo"
git remote add origin https://github.com/ezradesmonds/ZooLens.git
git push -u origin main
```
Jika `origin` sudah ada, gunakan `git remote -v` dan jangan tambah lagi. Jangan commit `.env`, dataset, atau model weights.
