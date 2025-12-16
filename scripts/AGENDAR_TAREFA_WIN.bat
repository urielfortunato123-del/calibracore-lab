@echo off
set "SCRIPT_PATH=%~dp0processar_alertas.py"
set "PYTHON_PATH=%~dp0..\backend\venv\Scripts\python.exe"

echo Criando tarefa agendada "CalibraCore_Alertas" para rodar diariamente as 08:00...

schtasks /create /tn "CalibraCore_Alertas" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /sc daily /st 08:00 /f

if %errorlevel% equ 0 (
    echo.
    echo [SUCESSO] Tarefa agendada com sucesso!
    echo Os alertas serao verificados todo dia as 08:00.
) else (
    echo.
    echo [ERRO] Nao foi possivel criar a tarefa. Execute este script como ADMINISTRADOR.
)

pause
