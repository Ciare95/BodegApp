@echo off
cd /d "%~dp0frontend"
call npm run build
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" collectstatic --noinput
echo.
echo Listo. Reinicia el backend (iniciar.bat) y entra a http://localhost:8000
