$ErrorActionPreference = 'Stop'
if (-not (Get-Command php -ErrorAction SilentlyContinue)) { throw 'PHP belum terpasang / tidak ada di PATH.' }
if (-not (Get-Command composer -ErrorAction SilentlyContinue)) { throw 'Composer belum terpasang / tidak ada di PATH.' }
if (Test-Path 'backend/artisan') { Write-Host 'Laravel sudah ada; skip.'; exit 0 }
if ((Test-Path 'backend') -and (Get-ChildItem 'backend' -Force | Measure-Object).Count -gt 0) { throw 'Folder backend tidak kosong. Jangan timpa file yang ada.' }
if (Test-Path 'backend') { Remove-Item 'backend' -Force }
composer create-project laravel/laravel backend
Set-Location backend
Copy-Item .env.example .env -Force
php artisan key:generate
php artisan migrate --force
npm install
Write-Host 'Laravel siap. Jalankan: cd backend; composer run dev'
