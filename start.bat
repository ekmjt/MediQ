@echo off
REM MediQueue Startup Script for Windows

echo Starting MediQueue...

REM Check if .env exists
if not exist .env (
    echo Error: .env file not found!
    echo Please create a .env file with your GEMINI_API_KEY
    exit /b 1
)

REM Start backend
echo Starting backend server...
cd backend
start "MediQueue Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend server...
cd frontend
start "MediQueue Frontend" cmd /k "npm run dev"
cd ..

echo.
echo Backend running on http://localhost:8000
echo Frontend running on http://localhost:3000
echo.
echo Close the command windows to stop the servers

