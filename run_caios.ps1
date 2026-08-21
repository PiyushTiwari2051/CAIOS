# CAIOS Startup Script for PowerShell
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Starting CAIOS MVP Shell (Local Adaptive Intelligence Layer)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

Write-Host "[1/3] Starting CAIOS Orchestrator (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".venv\Scripts\python.exe -m uvicorn orchestrator.app.main:app --host 127.0.0.1 --port 8000"

Write-Host "[2/3] Starting CAIOS LLM Reasoning Sandbox (Port 8001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".venv\Scripts\python.exe -m uvicorn llm-sandbox.service.main:app --host 127.0.0.1 --port 8001"

Write-Host "[3/3] Starting CAIOS Context Sensor..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".venv\Scripts\python.exe sensor/sensor.py"

Write-Host "Starting Dashboard on http://localhost:3000..." -ForegroundColor Cyan
Set-Location dashboard
npm start
