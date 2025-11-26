#!/bin/bash

###############################################################################
# Script para convertir archivos Oracle Forms (.fmb) a XML
# Requiere: Oracle Forms instalado con ORACLE_HOME configurado
###############################################################################

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar uso
show_usage() {
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  -f, --file <archivo.fmb>     Convertir un archivo específico"
    echo "  -d, --directory <directorio>  Convertir todos los .fmb en un directorio"
    echo "  -o, --output <directorio>     Directorio de salida (default: ./output)"
    echo "  -h, --help                    Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 -f mi_formulario.fmb"
    echo "  $0 -d ./forms -o ./xml_output"
    exit 1
}

# Verificar que ORACLE_HOME está configurado
check_oracle_home() {
    if [ -z "$ORACLE_HOME" ]; then
        echo -e "${RED}ERROR: ORACLE_HOME no está configurado${NC}"
        echo "Por favor, configura ORACLE_HOME antes de ejecutar este script"
        echo "Ejemplo: export ORACLE_HOME=/opt/oracle/middleware/forms"
        exit 1
    fi

    # Verificar que existe frmf2xml
    FRMF2XML="$ORACLE_HOME/bin/frmf2xml"
    if [ ! -f "$FRMF2XML" ]; then
        echo -e "${RED}ERROR: No se encuentra frmf2xml en $FRMF2XML${NC}"
        echo "Verifica que Oracle Forms esté instalado correctamente"
        exit 1
    fi

    echo -e "${GREEN}✓ ORACLE_HOME encontrado: $ORACLE_HOME${NC}"
}

# Convertir un archivo .fmb a .xml
convert_file() {
    local input_file=$1
    local output_dir=$2

    # Obtener nombre base sin extensión
    local basename=$(basename "$input_file" .fmb)
    local output_file="$output_dir/${basename}.xml"

    echo -e "${YELLOW}Convirtiendo: $input_file${NC}"

    # Ejecutar frmf2xml
    "$FRMF2XML" "$input_file" "$output_file" overwrite=yes

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Éxito: $output_file${NC}"
        return 0
    else
        echo -e "${RED}✗ Error al convertir: $input_file${NC}"
        return 1
    fi
}

# Variables por defecto
INPUT_FILE=""
INPUT_DIR=""
OUTPUT_DIR="./output"

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            INPUT_FILE="$2"
            shift 2
            ;;
        -d|--directory)
            INPUT_DIR="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo -e "${RED}Opción desconocida: $1${NC}"
            show_usage
            ;;
    esac
done

# Verificar que se proporcionó input
if [ -z "$INPUT_FILE" ] && [ -z "$INPUT_DIR" ]; then
    echo -e "${RED}ERROR: Debes especificar un archivo (-f) o directorio (-d)${NC}"
    show_usage
fi

# Verificar ORACLE_HOME
check_oracle_home

# Crear directorio de salida si no existe
mkdir -p "$OUTPUT_DIR"
echo -e "${GREEN}✓ Directorio de salida: $OUTPUT_DIR${NC}"

# Contador de éxitos y errores
SUCCESS=0
ERRORS=0

# Procesar archivo único
if [ -n "$INPUT_FILE" ]; then
    if [ ! -f "$INPUT_FILE" ]; then
        echo -e "${RED}ERROR: Archivo no encontrado: $INPUT_FILE${NC}"
        exit 1
    fi

    if convert_file "$INPUT_FILE" "$OUTPUT_DIR"; then
        SUCCESS=$((SUCCESS + 1))
    else
        ERRORS=$((ERRORS + 1))
    fi
fi

# Procesar directorio
if [ -n "$INPUT_DIR" ]; then
    if [ ! -d "$INPUT_DIR" ]; then
        echo -e "${RED}ERROR: Directorio no encontrado: $INPUT_DIR${NC}"
        exit 1
    fi

    echo -e "\n${YELLOW}Buscando archivos .fmb en: $INPUT_DIR${NC}"

    # Buscar todos los .fmb recursivamente
    while IFS= read -r -d '' file; do
        if convert_file "$file" "$OUTPUT_DIR"; then
            SUCCESS=$((SUCCESS + 1))
        else
            ERRORS=$((ERRORS + 1))
        fi
    done < <(find "$INPUT_DIR" -name "*.fmb" -print0)
fi

# Resumen
echo -e "\n${GREEN}=== RESUMEN ===${NC}"
echo -e "Conversiones exitosas: ${GREEN}$SUCCESS${NC}"
echo -e "Errores: ${RED}$ERRORS${NC}"

if [ $ERRORS -eq 0 ]; then
    exit 0
else
    exit 1
fi
