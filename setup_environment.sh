#!/bin/bash

###############################################################################
# Script para configurar variables de entorno de Oracle Forms
# Personaliza las rutas según tu instalación
###############################################################################

echo "=== Configuración de Variables de Entorno para Oracle Forms ==="

# PERSONALIZA ESTAS RUTAS SEGÚN TU INSTALACIÓN
ORACLE_HOME_PATH="/opt/oracle/middleware/forms"
JAVA_HOME_PATH="/usr/lib/jvm/java-8-openjdk-amd64"

# Verificar si ORACLE_HOME existe
if [ ! -d "$ORACLE_HOME_PATH" ]; then
    echo "⚠️  ADVERTENCIA: $ORACLE_HOME_PATH no existe"
    echo "Por favor, actualiza ORACLE_HOME_PATH en este script con la ruta correcta"
    echo ""
    echo "Rutas comunes de Oracle Forms:"
    echo "  - /opt/oracle/middleware/forms"
    echo "  - /u01/app/oracle/product/12.2.1/forms"
    echo "  - C:/Oracle/Middleware/Oracle_FRHome1 (Windows)"
    echo ""
    read -p "Ingresa la ruta de ORACLE_HOME: " ORACLE_HOME_PATH
fi

# Verificar si JAVA_HOME existe
if [ ! -d "$JAVA_HOME_PATH" ]; then
    echo "⚠️  ADVERTENCIA: $JAVA_HOME_PATH no existe"
    echo "Por favor, actualiza JAVA_HOME_PATH en este script con la ruta correcta"
    echo ""
    echo "Para encontrar Java en tu sistema:"
    echo "  - which java"
    echo "  - readlink -f \$(which java)"
    echo "  - /usr/lib/jvm/ (Linux)"
    echo ""
    read -p "Ingresa la ruta de JAVA_HOME: " JAVA_HOME_PATH
fi

# Exportar variables
export ORACLE_HOME="$ORACLE_HOME_PATH"
export JAVA_HOME="$JAVA_HOME_PATH"
export FORMS_PATH="$ORACLE_HOME/forms"
export PATH="$ORACLE_HOME/bin:$JAVA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$ORACLE_HOME/lib:$LD_LIBRARY_PATH"

# Mostrar configuración
echo ""
echo "✓ Variables de entorno configuradas:"
echo "  ORACLE_HOME=$ORACLE_HOME"
echo "  JAVA_HOME=$JAVA_HOME"
echo "  FORMS_PATH=$FORMS_PATH"
echo ""

# Verificar herramientas
echo "=== Verificación de Herramientas ==="

if [ -f "$ORACLE_HOME/bin/frmf2xml" ]; then
    echo "✓ frmf2xml encontrado"
else
    echo "✗ frmf2xml NO encontrado en $ORACLE_HOME/bin/frmf2xml"
fi

if command -v java &> /dev/null; then
    echo "✓ Java encontrado: $(java -version 2>&1 | head -n 1)"
else
    echo "✗ Java NO encontrado"
fi

echo ""
echo "=== Comandos Disponibles ==="
echo "Para hacer permanentes estas variables, añade lo siguiente a tu ~/.bashrc:"
echo ""
echo "# Oracle Forms Environment"
echo "export ORACLE_HOME=\"$ORACLE_HOME\""
echo "export JAVA_HOME=\"$JAVA_HOME\""
echo "export FORMS_PATH=\"\$ORACLE_HOME/forms\""
echo "export PATH=\"\$ORACLE_HOME/bin:\$JAVA_HOME/bin:\$PATH\""
echo "export LD_LIBRARY_PATH=\"\$ORACLE_HOME/lib:\$LD_LIBRARY_PATH\""
echo ""
echo "Luego ejecuta: source ~/.bashrc"
