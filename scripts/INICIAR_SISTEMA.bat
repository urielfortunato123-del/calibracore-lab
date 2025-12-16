@echo off
chcp 65001 >nul
title CalibraCore Lab - Sistema de Controle de Calibração

echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║     ⚗️  CalibraCore Lab                                       ║
echo  ║     Sistema Inteligente de Controle de Calibração            ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"
cd ..

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale Python 3.9 ou superior.
    echo        https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "backend\venv" (
    echo [INFO] Criando ambiente virtual...
    cd backend
    python -m venv venv
    cd ..
)

:: Activate virtual environment and install dependencies
echo [INFO] Ativando ambiente virtual...
call backend\venv\Scripts\activate.bat

:: Install dependencies if needed
echo [INFO] Verificando dependencias...
pip install -r backend\requirements.txt -q

:: Start the server
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  [OK] Iniciando servidor...
echo.
echo  Acesse: http://localhost:8000
echo.
echo  Login padrao:
echo    Email: admin@calibracore.lab
echo    Senha: admin123
echo.
echo  Pressione Ctrl+C para encerrar o servidor.
echo ═══════════════════════════════════════════════════════════════════
echo.

:: Wait a moment and open browser
start "" "http://localhost:8000"

:: Start server
cd backend
python run.py

pause
