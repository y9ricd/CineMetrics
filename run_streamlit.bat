@echo off
title CineMetrics AI - Streamlit App (Modul 14)
echo ========================================================
echo   CINEMETRICS AI - STREAMLIT APP (MODUL 14)
echo ========================================================
echo Dashboard URL: http://localhost:8501/
echo Tekan CTRL + C untuk menghentikan server.
echo.
"%~dp0venv\Scripts\python.exe" -m streamlit run "%~dp0app.py"
pause
