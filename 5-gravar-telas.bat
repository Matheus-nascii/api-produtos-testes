@echo off
title N3 - 5. Gravar telas do CRUD para o video
echo Liga a API, abre o Swagger e grava o CRUD (cerca de 1 a 3 minutos).
echo Feche antes a janela do 3-iniciar-api.bat, se estiver aberta.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\gravar-telas.ps1"
echo.
pause
