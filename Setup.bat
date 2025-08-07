@echo off
REM Fitra Portofolio One-Click Startup Script (servers only, assumes dependencies are installed)

REM --- Start Backend Server in New Terminal ---
start cmd /k "cd backend && call venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM --- Start Frontend Server in New Terminal ---
start cmd /k "cd frontend && npm run dev"

REM --- Close This Setup Window ---
exit
