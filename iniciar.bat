@echo off
set "BASE=%~dp0"
if "%BASE:~-1%"=="\" set "BASE=%BASE:~0,-1%"

:: Backend — usa el python del venv directamente, sin activar
start "" /min cmd /c ""%BASE%\venv\Scripts\python.exe" "%BASE%\manage.py" runserver 0.0.0.0:8000"

:: Frontend
start "" /min cmd /c "cd /d "%BASE%\frontend" && npm run build && npm run preview"

:: Esperar y abrir Chrome
timeout /t 15 /nobreak >nul
start chrome http://localhost
