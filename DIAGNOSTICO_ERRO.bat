@echo off
echo ========================================================
echo DIAGNOSTICO DE INICIALIZACAO - CALIBRACORE LAB
echo ========================================================
echo.
echo Tentando iniciar via Python (ABRIR_AGORA.bat)...
echo.

cd backend
if not exist "venv\Scripts\python.exe" (
    echo [ERRO] O Python nao foi encontrado na pasta venv.
    echo Isso acontece quando a pasta e copiada de outro computador.
    echo O ambiente virtual (venv) nao e portatil.
    echo.
) else (
    echo Iniciando aplicacao...
    venv\Scripts\python.exe desktop_app.py
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo [FALHA] O programa fechou com erro. Veja a mensagem acima.
    )
)

echo.
echo ========================================================
echo Tentando iniciar via Executavel (INICIAR.bat)...
echo ========================================================
cd ..
if exist "SistemaCalibraCore\CalibraCoreLab.exe" (
    "SistemaCalibraCore\CalibraCoreLab.exe"
) else (
    echo [ERRO] O executavel nao foi encontrado em SistemaCalibraCore\CalibraCoreLab.exe
)

echo.
echo ========================================================
echo FIM DO DIAGNOSTICO
echo Tire um print desta tela se houver erros.
echo ========================================================
pause
