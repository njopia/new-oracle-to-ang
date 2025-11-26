#!/bin/bash
# Script de inicio rápido para Linux/Mac
# Oracle Forms to Angular Migrator v3.0

echo "========================================"
echo "Oracle Forms to Angular Migrator v3.0"
echo "========================================"
echo

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    echo "Por favor instala Python 3.6+ desde https://www.python.org/"
    exit 1
fi

echo "[1/3] Verificando Python... OK"
echo

# Verificar que las dependencias están instaladas
echo "[2/3] Verificando dependencias..."
if ! python3 -c "import customtkinter" &> /dev/null; then
    echo
    echo "Las dependencias no están instaladas."
    echo "Instalando..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudieron instalar las dependencias"
        exit 1
    fi
fi

echo "[2/3] Verificando dependencias... OK"
echo

# Crear directorios necesarios
mkdir -p output temp logs

# Ejecutar la aplicación
echo "[3/3] Iniciando aplicación..."
echo
python3 main.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: La aplicación terminó con errores"
    exit 1
fi

echo
echo "Aplicación finalizada correctamente"
