@echo off
title N3 - 2. Testes unitarios e cobertura
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\rodar-testes.ps1"
echo.
pause
