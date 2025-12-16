@echo off
chcp 65001 >nul
title CalibraCore Lab - Importar Equipamentos

echo.
echo  ⚗️ CalibraCore Lab - Importar Equipamentos
echo  ═══════════════════════════════════════════════
echo.

cd /d "%~dp0"
cd ..

:: Activate virtual environment
call backend\venv\Scripts\activate.bat

:: Run seed script
python scripts\seed_equipamentos.py

echo.
pause
