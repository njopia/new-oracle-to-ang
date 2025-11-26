@echo off
REM Script de inicio rápido para Windows
REM Oracle Forms to Angular Migrator v3.0

echo ========================================
echo Oracle Forms to Angular Migrator v3.0
echo ========================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.6+ desde https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Verificando Python... OK
echo.

REM Verificar que las dependencias están instaladas
echo [2/3] Verificando dependencias...
python -c "import customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Las dependencias no están instaladas.
    echo Instalando...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

echo [2/3] Verificando dependencias... OK
echo.

REM Crear directorios necesarios
if not exist "output" mkdir output
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs

REM Ejecutar la aplicación
echo [3/3] Iniciando aplicación...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: La aplicación terminó con errores
    pause
    exit /b 1
)

echo.
echo Aplicación finalizada correctamente
pause
