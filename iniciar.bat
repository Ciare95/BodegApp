@echo off
echo Iniciando BodegApp...

:: Backend
start "Backend" cmd /k "call \"C:\Users\WIN 10\BodegApp\venv\Scripts\activate\" && python \"C:\Users\WIN 10\BodegApp\manage.py\" runserver 0.0.0.0:8000"

:: Frontend
start "Frontend" cmd /k "cd /d \"C:\Users\WIN 10\BodegApp\frontend\" && npm run preview"

echo.
echo BodegApp corriendo en:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost
echo.
