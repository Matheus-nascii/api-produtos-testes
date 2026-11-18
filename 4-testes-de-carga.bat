@echo off
title N3 - 4. Testes de carga (k6)
echo Roda Smoke, Average Load e Stress em sequencia (cerca de 22 minutos).
echo Deixe o notebook no carregador e com os outros programas fechados.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\rodar-k6.ps1" %*
echo.
pause
