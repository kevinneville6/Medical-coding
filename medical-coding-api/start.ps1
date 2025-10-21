Write-Host "Starting Medical Coding API..." -ForegroundColor Green

# Check if virtual environment exists and activate it
if (Test-Path "venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Please create it with: python -m venv venv" -ForegroundColor Red
    exit 1
}

# Run the API
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
python main.py
