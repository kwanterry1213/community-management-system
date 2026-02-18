@echo off
echo ===================================================
echo DEBUG MODE: Starting Community Management System
echo ===================================================

echo [DEBUG] Checking Python version...
python --version
where python

echo [DEBUG] Checking dependencies...
python -c "import fastapi; import uvicorn; import python_multipart; print('Dependencies OK')"

echo [DEBUG] Starting Uvicorn...
cd /d "%~dp0"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server failed to start! Error code: %ERRORLEVEL%
    echo Please check the error message above.
)

pause
