@echo off
title CalibraCore Lab - Auto-Sync GitHub
echo ======================================================
echo CalibraCore Lab - Sincronismo Automatico
echo ======================================================
echo.
echo Iniciando monitoramento de arquivos...
echo Seus arquivos serao enviados ao GitHub sempre que salvos.
echo Nao feche esta janela enquanto estiver trabalhando.
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0scripts\auto_sync.ps1"

echo.
echo Ocorreu um erro ou o processo foi encerrado.
pause
