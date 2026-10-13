$ErrorActionPreference = 'Stop'
Set-Location ai-service
python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 belum tersedia. Instal Python 3.11 dan ulangi.' }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
Write-Host 'Jalankan: cd ai-service; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001'
