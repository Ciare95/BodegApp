@echo off
set "BASE=%~dp0"
if "%BASE:~-1%"=="\" set "BASE=%BASE:~0,-1%"

:: Lanzar backend oculto
set "CMD_BACK="%BASE%\venv\Scripts\activate" && python "%BASE%\manage.py" runserver 0.0.0.0:8000"
powershell -WindowStyle Hidden -Command "Start-Process cmd -ArgumentList '/c %BASE%\venv\Scripts\activate && python %BASE%\manage.py runserver 0.0.0.0:8000' -WindowStyle Hidden"

:: Lanzar frontend oculto
powershell -WindowStyle Hidden -Command "Start-Process cmd -ArgumentList '/c cd /d %BASE%\frontend && npm run build && npm run preview' -WindowStyle Hidden"

:: Esperar y abrir Chrome
timeout /t 15 /nobreak >nul
start chrome http://localhost
