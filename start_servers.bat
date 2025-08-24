@echo off
echo Starting SaaS Platform Servers...
echo ========================================

echo Starting Django Backend Server...
start "Django Backend" cmd /c "cd backend && python manage.py runserver --settings=saas_project.settings_sqlite"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo Starting React Frontend Server...
start "React Frontend" cmd /c "cd frontend && npm start"

echo ========================================
echo Servers are starting up!
echo.
echo Backend:  http://localhost:8000 (API only)
echo Frontend: http://localhost:3000 (Main App)
echo.
echo Wait about 10-15 seconds for React to fully start up.
echo Then open your browser and go to: http://localhost:3000
echo.
echo Press any key to continue...
pause 