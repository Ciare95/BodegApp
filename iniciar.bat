@echo off
set "BASE=%~dp0"
:: Quitar la barra final si existe
if "%BASE:~-1%"=="\" set "BASE=%BASE:~0,-1%"

:: Backend
start "Backend" cmd /k ""%BASE%\venv\Scripts\activate" && python "%BASE%\manage.py" runserver 0.0.0.0:8000"

:: Frontend
start "Frontend" cmd /k "cd /d "%BASE%\frontend" && npm run preview"

:: Esperar 5 segundos y abrir Chrome
timeout /t 5 /nobreak >nul
start chrome http://localhost
