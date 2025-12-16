@echo off
chcp 65001 >nul
title CalibraCore Lab - Processar Alertas

echo.
echo  ⚗️ CalibraCore Lab - Processamento de Alertas
echo  ═══════════════════════════════════════════════
echo.

cd /d "%~dp0"
cd ..

:: Activate virtual environment
call backend\venv\Scripts\activate.bat

:: Run alert processing
python scripts\processar_alertas.py

echo.
echo Processamento concluido!
pause
