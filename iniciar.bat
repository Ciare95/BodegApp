@echo off
echo Iniciando BodegApp...

:: Activar entorno virtual
call venv\Scripts\activate

:: Backend
start "Backend" cmd /k "python manage.py runserver 0.0.0.0:8000"

:: Frontend
cd frontend
start "Frontend" cmd /k "npm run preview"
cd ..

echo.
echo BodegApp corriendo en:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost
echo.
pause