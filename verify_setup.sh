#!/bin/bash

###############################################################################
# Script de verificación rápida para Oracle Forms
# Verifica que todo esté configurado correctamente antes de convertir
###############################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Verificación de Configuración de Oracle Forms ===${NC}\n"

ERRORS=0
WARNINGS=0

# Verificar ORACLE_HOME
echo -e "${YELLOW}[1/6] Verificando ORACLE_HOME...${NC}"
if [ -z "$ORACLE_HOME" ]; then
    echo -e "${RED}✗ ORACLE_HOME no está configurado${NC}"
    echo "   Ejecuta: export ORACLE_HOME=/ruta/a/oracle/forms"
    ERRORS=$((ERRORS + 1))
elif [ ! -d "$ORACLE_HOME" ]; then
    echo -e "${RED}✗ ORACLE_HOME apunta a un directorio inexistente: $ORACLE_HOME${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ ORACLE_HOME: $ORACLE_HOME${NC}"
fi

# Verificar frmf2xml
echo -e "\n${YELLOW}[2/6] Verificando frmf2xml...${NC}"
if command -v frmf2xml &> /dev/null; then
    FRMF2XML_PATH=$(which frmf2xml)
    echo -e "${GREEN}✓ frmf2xml encontrado: $FRMF2XML_PATH${NC}"
elif [ -n "$ORACLE_HOME" ] && [ -f "$ORACLE_HOME/bin/frmf2xml" ]; then
    echo -e "${GREEN}✓ frmf2xml encontrado: $ORACLE_HOME/bin/frmf2xml${NC}"
    echo -e "${YELLOW}  ⚠ Considera añadir \$ORACLE_HOME/bin al PATH${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${RED}✗ frmf2xml no encontrado${NC}"
    echo "   Verifica que Oracle Forms esté instalado correctamente"
    ERRORS=$((ERRORS + 1))
fi

# Verificar JAVA_HOME
echo -e "\n${YELLOW}[3/6] Verificando JAVA_HOME...${NC}"
if [ -z "$JAVA_HOME" ]; then
    echo -e "${YELLOW}⚠ JAVA_HOME no está configurado${NC}"
    echo "   Aunque no es crítico, se recomienda configurarlo"
    WARNINGS=$((WARNINGS + 1))
elif [ ! -d "$JAVA_HOME" ]; then
    echo -e "${YELLOW}⚠ JAVA_HOME apunta a un directorio inexistente: $JAVA_HOME${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓ JAVA_HOME: $JAVA_HOME${NC}"
fi

# Verificar Java
echo -e "\n${YELLOW}[4/6] Verificando Java...${NC}"
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    echo -e "${GREEN}✓ Java encontrado: $JAVA_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Java no encontrado en PATH${NC}"
    echo "   Considera instalar Java y añadirlo al PATH"
    WARNINGS=$((WARNINGS + 1))
fi

# Verificar LD_LIBRARY_PATH
echo -e "\n${YELLOW}[5/6] Verificando LD_LIBRARY_PATH...${NC}"
if [ -n "$LD_LIBRARY_PATH" ] && [[ "$LD_LIBRARY_PATH" == *"$ORACLE_HOME"* ]]; then
    echo -e "${GREEN}✓ LD_LIBRARY_PATH incluye ORACLE_HOME${NC}"
elif [ -n "$ORACLE_HOME" ] && [ -d "$ORACLE_HOME/lib" ]; then
    echo -e "${YELLOW}⚠ LD_LIBRARY_PATH no incluye \$ORACLE_HOME/lib${NC}"
    echo "   Si tienes problemas, ejecuta: export LD_LIBRARY_PATH=\$ORACLE_HOME/lib:\$LD_LIBRARY_PATH"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${YELLOW}⚠ LD_LIBRARY_PATH no está configurado${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Verificar PATH
echo -e "\n${YELLOW}[6/6] Verificando PATH...${NC}"
if [ -n "$ORACLE_HOME" ] && [[ "$PATH" == *"$ORACLE_HOME/bin"* ]]; then
    echo -e "${GREEN}✓ PATH incluye \$ORACLE_HOME/bin${NC}"
elif [ -n "$ORACLE_HOME" ]; then
    echo -e "${YELLOW}⚠ PATH no incluye \$ORACLE_HOME/bin${NC}"
    echo "   Ejecuta: export PATH=\$ORACLE_HOME/bin:\$PATH"
    WARNINGS=$((WARNINGS + 1))
fi

# Resumen
echo -e "\n${BLUE}=== RESUMEN ===${NC}"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ ¡Todo está configurado correctamente!${NC}"
    echo -e "\nPuedes usar el script convert_fmb_to_xml.sh sin problemas."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Configuración funcional con $WARNINGS advertencia(s)${NC}"
    echo -e "\nPuedes usar el script, pero considera resolver las advertencias."
    exit 0
else
    echo -e "${RED}✗ Encontrados $ERRORS error(es) y $WARNINGS advertencia(s)${NC}"
    echo -e "\nPor favor, resuelve los errores antes de continuar."
    echo -e "\nPara ayuda, consulta el README.md o ejecuta:"
    echo -e "  ./setup_environment.sh"
    exit 1
fi
