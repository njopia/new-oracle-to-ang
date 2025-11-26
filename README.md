# Conversor de Oracle Forms (.fmb) a XML

Este proyecto proporciona herramientas en Python para convertir archivos Oracle Forms binarios (.fmb) a formato XML.

## Requisitos Previos

1. **Python 3.6+** instalado
2. **Oracle Forms** instalado (Forms Developer Suite 10g, 11g, o 12c)
3. **Java JDK** instalado y configurado
4. Variables de entorno configuradas:
   - `ORACLE_HOME`: Ruta de instalación de Oracle Forms
   - `JAVA_HOME`: Ruta de instalación de Java
   - `PATH`: Debe incluir `$ORACLE_HOME/bin` y `$JAVA_HOME/bin`

## Verificación de la Instalación

Antes de usar el script, verifica que tienes todo configurado:

```bash
# Verificar Python
python3 --version

# Verificar ORACLE_HOME
echo $ORACLE_HOME
# Ejemplo de salida: /opt/oracle/middleware/forms

# Verificar que frmf2xml existe
ls -l $ORACLE_HOME/bin/frmf2xml

# Verificar Java
java -version

# O usar el script de verificación automática
python3 verify_setup.py
```

## Configuración de Variables de Entorno

Si no están configuradas, añade las siguientes líneas a tu `~/.bashrc` o `~/.bash_profile`:

```bash
# Oracle Forms
export ORACLE_HOME=/opt/oracle/middleware/forms
export PATH=$ORACLE_HOME/bin:$PATH

# Java
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Oracle Forms adicionales (opcional)
export FORMS_PATH=$ORACLE_HOME/forms
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH
```

Luego recarga el perfil:
```bash
source ~/.bashrc
```

## Uso del Script Python

### Convertir un archivo único

```bash
python3 convert_fmb_to_xml.py -f mi_formulario.fmb
```

El archivo XML se generará en `./output/mi_formulario.xml`

### Convertir todos los .fmb de un directorio

```bash
python3 convert_fmb_to_xml.py -d ./forms_directory -o ./xml_output
```

### Opciones disponibles

```bash
python3 convert_fmb_to_xml.py --help
```

- `-f, --file <archivo.fmb>`: Convertir un archivo específico
- `-d, --directory <directorio>`: Convertir todos los .fmb en un directorio (recursivo)
- `-o, --output <directorio>`: Especificar directorio de salida (default: ./output)
- `-h, --help`: Mostrar ayuda

### Scripts auxiliares

**Verificar configuración:**
```bash
python3 verify_setup.py
```

**Asistente de configuración:**
```bash
python3 setup_environment.py
```

## Método Alternativo: Conversión Manual

Si prefieres convertir manualmente usando la utilidad de Oracle:

```bash
# Sintaxis básica
frmf2xml source.fmb dest.xml overwrite=yes

# Ejemplo
frmf2xml mi_formulario.fmb mi_formulario.xml overwrite=yes
```

## Conversión de XML a FMB (reversa)

Para convertir de vuelta XML a FMB:

```bash
frmxml2bin source.xml dest.fmb overwrite=yes
```

## Estructura de Directorios Recomendada

```
proyecto/
├── forms/                    # Archivos .fmb originales
│   ├── formulario1.fmb
│   └── formulario2.fmb
├── xml_output/               # XMLs generados
│   ├── formulario1.xml
│   └── formulario2.xml
├── convert_fmb_to_xml.py     # Script principal (Python)
├── verify_setup.py           # Verificación (Python)
├── setup_environment.py      # Configuración (Python)
├── convert_fmb_to_xml.sh     # Script principal (Bash - legacy)
└── README.md
```

## Solución de Problemas

### Error: "ORACLE_HOME no está configurado"

**Solución**: Configura la variable de entorno ORACLE_HOME:
```bash
export ORACLE_HOME=/ruta/a/oracle/forms
```

### Error: "frmf2xml: command not found"

**Solución**: Verifica que el binario existe y que `$ORACLE_HOME/bin` está en tu PATH:
```bash
ls $ORACLE_HOME/bin/frmf2xml
export PATH=$ORACLE_HOME/bin:$PATH
```

### Error: "FRM-18108: Failed to load the following objects"

**Posibles causas**:
1. El archivo .fmb está corrupto
2. Falta configurar FORMS_PATH para librerías (.pll)
3. Problemas de compatibilidad de versiones

**Solución**:
```bash
export FORMS_PATH=/ruta/a/librerias/pll
```

### Error relacionado con librerías compartidas

**Solución**: Configura LD_LIBRARY_PATH:
```bash
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH
```

## Próximos Pasos

Una vez convertidos los formularios a XML, puedes:

1. **Control de versiones**: Los archivos XML son text-based y funcionan mejor con Git
2. **Análisis**: Parsear el XML para extraer información de los formularios
3. **Migración**: Usar el XML como base para migrar a otras tecnologías (ej. Angular)
4. **Documentación**: Generar documentación automática de los formularios

## Notas Importantes

- Los archivos .fmb son binarios y no pueden ser versionados eficientemente en Git
- Los archivos XML son texto plano y son ideales para control de versiones
- Siempre mantén una copia de respaldo de tus archivos .fmb originales
- El proceso de conversión es determinístico: el mismo .fmb siempre genera el mismo XML

## Recursos Adicionales

- [Oracle Forms Documentation](https://docs.oracle.com/en/middleware/developer-tools/forms/)
- [Oracle Forms to XML Conversion Guide](https://docs.oracle.com/cd/E14571_01/core.1111/e10043/frmf2xml.htm)

## Licencia

Este script es de código abierto y puede ser usado libremente para proyectos personales y comerciales.
