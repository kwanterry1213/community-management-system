#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

echo "Starting Community Management System (H5 Backend)..."
echo "Server will be accessible at http://localhost:8000"
echo "To stop the server, press Ctrl+C"

# Check if python3 is available
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

# Run the server
$PYTHON_CMD -m uvicorn app:app --host 0.0.0.0 --port 8000
