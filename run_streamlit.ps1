Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   CINEMETRICS AI - STREAMLIT APP (MODUL 14)            " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Dashboard URL: http://localhost:8501/" -ForegroundColor Green
Write-Host "Tekan CTRL + C untuk menghentikan server.`n" -ForegroundColor Gray

& "$PSScriptRoot\venv\Scripts\python.exe" -m streamlit run "$PSScriptRoot\app.py"
