@echo off
title CAIOS - Casual Adaptive Intelligence Operating System
echo ======================================================================
echo   Starting CAIOS MVP Shell (Local Adaptive Intelligence Layer)
echo ======================================================================

echo [1/3] Starting CAIOS Orchestrator (FastAPI on Port 8000)...
start "CAIOS Orchestrator" cmd /k ".venv\Scripts\python.exe -m uvicorn orchestrator.app.main:app --host 127.0.0.1 --port 8000"

echo [2/3] Starting CAIOS LLM Reasoning Sandbox (Port 8001)...
start "CAIOS LLM Sandbox" cmd /k ".venv\Scripts\python.exe -m uvicorn llm-sandbox.service.main:app --host 127.0.0.1 --port 8001"

echo [3/3] Starting CAIOS Context Sensor...
start "CAIOS Sensor" cmd /k ".venv\Scripts\python.exe sensor/sensor.py"

echo Starting CAIOS Web Dashboard on http://localhost:3000...
cd dashboard && npm start
