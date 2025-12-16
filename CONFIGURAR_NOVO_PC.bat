@echo off
echo ==========================================
echo CONFIGURANDO CALIBRACORE LAB
echo Para usar em um novo computador
echo ==========================================
echo.

echo Passo 1: Verificando Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale o Python (python.org) e marque a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit
)

cd backend

if exist "venv" (
    echo.
    echo Passo 2: Limpando configuracao antiga...
    echo (Ambientes virtuais nao podem ser copiados entre PCs)
    rmdir /s /q "venv"
)

echo.
echo Passo 3: Criando novo ambiente virtual...
python -m venv venv

echo.
echo Passo 4: Instalando dependencias...
venv\Scripts\pip install -r requirements.txt

echo.
echo ==========================================
echo TUDO PRONTO!
echo Agora voce pode usar o arquivo "ABRIR_AGORA.bat"
echo ==========================================
pause
