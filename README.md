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

**Penting:** endpoint `/predict` sengaja mengembalikan HTTP 503 sampai bobot model yang benar tersedia dan `MODEL_PATH` dikonfigurasi. Belum ada trained model, integrasi Laravel-FastAPI, halaman Scanner/Factsheet/Safari, ataupun deployment production di starter ini.

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
