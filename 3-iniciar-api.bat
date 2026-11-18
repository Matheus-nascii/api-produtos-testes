@echo off
title N3 - 3. API ligada em http://localhost:8000
cd /d "%~dp0"
echo API ligada em http://localhost:8000   -   Swagger: http://localhost:8000/docs
echo Para desligar a API, feche esta janela.
echo.
".venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000
pause
