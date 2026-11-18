@echo off
title N3 - 1. Preparar ambiente
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\preparar-ambiente.ps1"
echo.
pause
