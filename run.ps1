Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   CINEMETRICS AI - PREDICTIVE ENGINE SERVER            " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Dashboard URL: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "Tekan CTRL + C untuk menghentikan server.`n" -ForegroundColor Gray

& "$PSScriptRoot\venv\Scripts\python.exe" "$PSScriptRoot\manage.py" migrate --noinput
& "$PSScriptRoot\venv\Scripts\python.exe" "$PSScriptRoot\manage.py" runserver
