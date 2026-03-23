@echo off
set BASE=C:\Users\WIN 10\BodegApp

:: Backend
start "Backend" cmd /k "%BASE%\venv\Scripts\activate && python %BASE%\manage.py runserver 0.0.0.0:8000"

:: Frontend
start "Frontend" cmd /k "cd /d %BASE%\frontend && npm run preview"
