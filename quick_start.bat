@echo off
echo ===========================================
echo Starting SaaS Platform - Quick Start
echo ===========================================
echo.

echo Step 1: Starting Django Backend...
cd backend
start "Django Backend Server" cmd /k "python manage.py runserver --settings=saas_project.settings_sqlite"
cd ..

echo Waiting 5 seconds for Django to start...
timeout /t 5 /nobreak > nul

echo Step 2: Starting React Frontend...
cd frontend
start "React Frontend Server" cmd /k "node node_modules/react-scripts/bin/react-scripts.js start"
cd ..

echo.
echo ===========================================
echo SERVERS STARTING...
echo ===========================================
echo.
echo Django Backend: http://localhost:8000
echo React Frontend: http://localhost:3000
echo.
echo Wait 15-20 seconds for React to compile, then:
echo 1. Open browser
echo 2. Go to: http://localhost:3000
echo 3. Test the signup flow!
echo.
echo Both servers will run in separate windows.
echo Close those windows to stop the servers.
echo.
pause 