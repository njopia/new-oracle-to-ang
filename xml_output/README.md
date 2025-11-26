# Directorio de Salida XML

Este directorio contiene los archivos XML generados a partir de los formularios Oracle Forms (.fmb).

## Estructura

Los archivos XML mantendrán la misma estructura de nombres que los archivos .fmb originales:

```
xml_output/
├── formulario1.xml
├── formulario2.xml
└── formulario3.xml
```

## Ventajas del formato XML

1. **Versionable**: Archivos de texto que funcionan bien con Git
2. **Legible**: Estructura clara y navegable
3. **Procesable**: Fácil de parsear con herramientas estándar
4. **Migrable**: Base para conversión a otras tecnologías

## Uso de los archivos XML

### Ver estructura
```bash
# Ver inicio del archivo
head -n 50 formulario1.xml

# Buscar elementos específicos
grep -n "Block" formulario1.xml
grep -n "Item" formulario1.xml
```

### Analizar con herramientas XML
```bash
# Formatear para mejor lectura
xmllint --format formulario1.xml | less

# Extraer información específica con xmlstarlet
xmlstarlet sel -t -v "//Block/@Name" formulario1.xml
```

### Convertir de vuelta a .fmb
```bash
frmxml2bin formulario1.xml formulario1_nuevo.fmb overwrite=yes
```

## Próximos pasos

1. **Analizar**: Examinar la estructura de los formularios
2. **Documentar**: Generar documentación automática
3. **Migrar**: Usar como base para migración (ej. a Angular)
4. **Versionar**: Hacer commit de los cambios

```bash
git add .
git commit -m "Añadir XML de formularios Oracle Forms"
git push
```
