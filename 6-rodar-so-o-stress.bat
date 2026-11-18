@echo off
title N3 - 6. Somente o Stress Test (k6)
echo Roda so o Stress Test (cerca de 11 minutos), reiniciando a API antes.
echo Deixe o notebook no carregador e com os outros programas fechados.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\rodar-k6.ps1" -Testes stress
echo.
pause
