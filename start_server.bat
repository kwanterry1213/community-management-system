@echo off
echo Starting Community Management System (H5 Backend)...
echo Server will be accessible at http://localhost:8000
echo To stop the server, press Ctrl+C

cd /d "%~dp0"
python -m uvicorn app:app --host 0.0.0.0 --port 8000

pause
