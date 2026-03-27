@echo off
set "BASE=%~dp0"
if "%BASE:~-1%"=="\" set "BASE=%BASE:~0,-1%"

:: Liberar puerto 80
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":80 "') do taskkill /PID %%a /F >nul 2>&1

:: Backend
start "" /min cmd /c ""%BASE%\venv\Scripts\python.exe" "%BASE%\manage.py" runserver 0.0.0.0:8000"

:: Frontend
start "" /min cmd /c "cd /d "%BASE%\frontend" && npm run build && npm run preview -- --port 80"

:: Esperar y abrir Chrome
timeout /t 15 /nobreak >nul
start chrome http://localhost
