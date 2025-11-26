# Comandos Útiles para Oracle Forms

Esta es una referencia rápida de comandos útiles para trabajar con Oracle Forms y archivos XML.

## Comandos de Conversión

### FMB a XML
```bash
# Convertir un archivo
frmf2xml source.fmb dest.xml overwrite=yes

# Con rutas completas
frmf2xml /ruta/completa/formulario.fmb /ruta/salida/formulario.xml overwrite=yes

# Conversión en lote con script
./convert_fmb_to_xml.sh -d forms -o xml_output
```

### XML a FMB
```bash
# Convertir de vuelta a binario
frmxml2bin source.xml dest.fmb overwrite=yes

# Ejemplo
frmxml2bin formulario.xml formulario_nuevo.fmb overwrite=yes
```

## Compilación de Formularios

### Compilar FMB a FMX (ejecutable)
```bash
# Compilar un formulario
frmcmp module=formulario.fmb userid=usuario/password@db batch=yes compile_all=yes

# Sin conexión a base de datos
frmcmp module=formulario.fmb batch=yes compile_all=yes

# Compilar con archivo de configuración
frmcmp module=formulario.fmb userid=usuario/password@db module_type=form batch=yes
```

## Comandos de Análisis XML

### Ver estructura del XML
```bash
# Ver primeras líneas
head -n 100 formulario.xml

# Ver con formato bonito
xmllint --format formulario.xml | less

# Contar elementos
grep -c "<Block>" formulario.xml
grep -c "<Item>" formulario.xml
```

### Buscar elementos específicos
```bash
# Buscar todos los bloques
grep "<Block Name=" formulario.xml

# Buscar items específicos
grep "Name=\"EMPLOYEE_ID\"" formulario.xml

# Buscar triggers
grep "<Trigger>" formulario.xml

# Buscar con contexto
grep -A 5 -B 5 "TriggerName=\"WHEN-NEW-FORM-INSTANCE\"" formulario.xml
```

### Extraer información con xmlstarlet
```bash
# Instalar xmlstarlet si no está disponible
# sudo apt-get install xmlstarlet  # Ubuntu/Debian
# brew install xmlstarlet          # macOS

# Listar todos los nombres de bloques
xmlstarlet sel -t -v "//Block/@Name" -n formulario.xml

# Listar todos los items
xmlstarlet sel -t -v "//Item/@Name" -n formulario.xml

# Extraer información de triggers
xmlstarlet sel -t -m "//Trigger" -v "@Name" -o ": " -v "TriggerText" -n formulario.xml
```

## Comandos de Gestión de Librerías

### Convertir Librerías PLL
```bash
# PLL (binario) a PLD (texto)
frmcmp module=libreria.pll userid=usuario/password@db module_type=library batch=yes

# PLD a PLL
# Similar proceso con frmcmp
```

## Comandos de Búsqueda

### Buscar en múltiples archivos
```bash
# Buscar un término en todos los XMLs
grep -r "EMPLOYEE_TABLE" xml_output/

# Buscar con número de línea
grep -rn "WHEN-BUTTON-PRESSED" xml_output/

# Buscar y mostrar solo nombres de archivo
grep -rl "COMMIT_FORM" xml_output/

# Buscar con contexto
grep -r -A 3 -B 3 "DATABASE_ITEM" xml_output/
```

### Buscar formularios que usan un objeto
```bash
# Encontrar formularios que usan un bloque específico
for file in xml_output/*.xml; do
    if grep -q "EMPLOYEE_BLOCK" "$file"; then
        echo "Encontrado en: $file"
    fi
done
```

## Comandos de Estadísticas

### Análisis de formularios
```bash
# Contar bloques por formulario
for file in xml_output/*.xml; do
    echo "$file: $(grep -c "<Block>" "$file") bloques"
done

# Contar items totales
find xml_output -name "*.xml" -exec grep -o "<Item>" {} \; | wc -l

# Listar formularios por tamaño
ls -lhS xml_output/*.xml
```

## Comandos Git

### Versionado
```bash
# Añadir XMLs al repo
git add xml_output/*.xml

# Commit con mensaje descriptivo
git commit -m "Convertir formularios Oracle a XML"

# Ver diferencias entre versiones
git diff HEAD~1 xml_output/formulario.xml

# Ver historial de un archivo
git log --follow xml_output/formulario.xml
```

## Comandos de Respaldo

### Crear respaldos
```bash
# Respaldar FMBs originales
tar -czf backup_fmb_$(date +%Y%m%d).tar.gz forms/

# Respaldar XMLs
tar -czf backup_xml_$(date +%Y%m%d).tar.gz xml_output/

# Respaldar todo el proyecto
tar -czf backup_completo_$(date +%Y%m%d).tar.gz --exclude='.git' .
```

### Restaurar respaldos
```bash
# Extraer respaldo
tar -xzf backup_fmb_20250126.tar.gz
```

## Comandos de Limpieza

### Limpiar archivos temporales
```bash
# Eliminar respaldos automáticos de Forms
find . -name "*.fmb~" -delete
find . -name "*.fmx" -delete

# Limpiar directorio output
rm -rf xml_output/*
```

## Comandos de Verificación

### Verificar instalación
```bash
# Verificar ORACLE_HOME
echo $ORACLE_HOME

# Verificar que frmf2xml existe
which frmf2xml
ls -l $ORACLE_HOME/bin/frmf2xml

# Verificar versión de Java
java -version

# Ejecutar script de verificación
./verify_setup.sh
```

## Scripts Personalizados

### Convertir y respaldar
```bash
#!/bin/bash
# Convertir todos los FMB y crear respaldo de XMLs anteriores

# Respaldar XMLs existentes
if [ -d "xml_output" ] && [ "$(ls -A xml_output)" ]; then
    tar -czf "backup_xml_$(date +%Y%m%d_%H%M%S).tar.gz" xml_output/
fi

# Convertir
./convert_fmb_to_xml.sh -d forms -o xml_output

# Commit automático
git add xml_output/
git commit -m "Actualizar XMLs - $(date +%Y-%m-%d)"
```

### Generar reporte de formularios
```bash
#!/bin/bash
# Generar reporte de todos los formularios

echo "=== Reporte de Formularios ==="
echo "Generado: $(date)"
echo ""

for file in xml_output/*.xml; do
    nombre=$(basename "$file" .xml)
    bloques=$(grep -c "<Block>" "$file")
    items=$(grep -c "<Item>" "$file")
    triggers=$(grep -c "<Trigger>" "$file")

    echo "Formulario: $nombre"
    echo "  Bloques: $bloques"
    echo "  Items: $items"
    echo "  Triggers: $triggers"
    echo ""
done
```

## Referencias

- Manual de Oracle Forms: `$ORACLE_HOME/doc/`
- Ayuda de frmf2xml: `frmf2xml -help`
- Documentación XML: https://www.w3.org/XML/
