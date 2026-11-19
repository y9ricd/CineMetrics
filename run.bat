@echo off
title CineMetrics AI - Predictive Movie Intelligence
echo ========================================================
echo   CINEMETRICS AI - PREDICTIVE ENGINE SERVER
echo ========================================================
echo Dashboard URL: http://127.0.0.1:8000/
echo Tekan CTRL + C untuk menghentikan server.
echo.
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" migrate --noinput
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" runserver
pause
