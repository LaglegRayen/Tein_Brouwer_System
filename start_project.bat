@echo off
echo ========================================
echo SaaS Platform Setup and Start Guide
echo ========================================
echo.

echo Step 1: Start PostgreSQL Service
echo Run this command as Administrator:
echo   net start postgresql-x64-17
echo.
echo If PostgreSQL is not installed, download from:
echo   https://www.postgresql.org/download/windows/
echo.

echo Step 2: Create Database
echo Run this in psql:
echo   CREATE DATABASE saas_db;
echo.

echo Step 3: Set Environment Variables
echo Copy backend\env.example to backend\.env and update with your settings
echo.

echo Step 4: Install Python Dependencies
echo   cd backend
echo   pip install -r ..\requirements.txt
echo.

echo Step 5: Run Migrations
echo   python manage.py makemigrations
echo   python manage.py migrate
echo.

echo Step 6: Start Backend Server (in one terminal)
echo   python manage.py runserver
echo.

echo Step 7: Start Frontend Server (in another terminal)
echo   cd frontend
echo   npm install
echo   npm start
echo.

echo Step 8: Access the Application
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   Admin Panel: http://localhost:8000/admin
echo.

echo ========================================
echo Press any key to continue...
pause 