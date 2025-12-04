$ErrorActionPreference = "Stop"

Write-Host "Starting CodeIT Chatbot..." -ForegroundColor Green

# Define paths
$Root = Get-Location
$VenvPython = "$Root\.venv\Scripts\python.exe"
$BackendDir = "$Root\codeIT"
$FrontendDir = "$Root\codeIT\frontend"

# Check if venv exists
if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment not found at $VenvPython. Please run setup first."
    exit 1
}

# Start Backend
Write-Host "Starting Backend Server..." -ForegroundColor Cyan
Start-Process -FilePath $VenvPython -ArgumentList "-m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000" -WorkingDirectory $BackendDir

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Set-Location $FrontendDir
Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory $FrontendDir

Write-Host "Application is running!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:5173 (or 5174 if busy)"
Write-Host "Press Ctrl+C to stop the servers (you may need to close the terminal window to fully kill processes)."
