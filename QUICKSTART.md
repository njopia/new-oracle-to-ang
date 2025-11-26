# Guía Rápida de Inicio

Esta guía te ayudará a convertir tus archivos Oracle Forms (.fmb) a XML en minutos.

## Paso 1: Verificar Requisitos

Ejecuta el script de verificación:

```bash
./verify_setup.sh
```

Si ves errores, continúa al Paso 2. Si todo está OK, salta al Paso 3.

## Paso 2: Configurar Variables de Entorno

### Opción A: Configuración Automática

```bash
./setup_environment.sh
```

Este script te guiará en la configuración.

### Opción B: Configuración Manual

Edita el archivo `example_config.env` con tus rutas:

```bash
# Edita el archivo
nano example_config.env

# Luego carga las variables
source example_config.env
```

### Opción C: Configuración Permanente

Añade a tu `~/.bashrc`:

```bash
export ORACLE_HOME=/ruta/a/oracle/forms
export JAVA_HOME=/ruta/a/java
export PATH=$ORACLE_HOME/bin:$JAVA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH
```

Luego:
```bash
source ~/.bashrc
```

## Paso 3: Organizar tus Archivos

Crea la siguiente estructura:

```
tu-proyecto/
├── forms/              # Coloca aquí tus archivos .fmb
│   ├── formulario1.fmb
│   └── formulario2.fmb
└── xml_output/         # Aquí se generarán los XML
```

```bash
mkdir -p forms xml_output
# Copia tus archivos .fmb a la carpeta forms/
```

## Paso 4: Convertir

### Convertir un solo archivo:

```bash
./convert_fmb_to_xml.sh -f forms/mi_formulario.fmb
```

### Convertir todos los archivos de un directorio:

```bash
./convert_fmb_to_xml.sh -d forms -o xml_output
```

### Con ruta personalizada de salida:

```bash
./convert_fmb_to_xml.sh -f forms/mi_formulario.fmb -o mis_xmls
```

## Paso 5: Verificar Resultados

```bash
ls -lh xml_output/
```

Deberías ver archivos `.xml` correspondientes a tus archivos `.fmb`.

## Conversión Manual (Alternativa)

Si prefieres hacerlo manualmente con el comando de Oracle:

```bash
frmf2xml forms/mi_formulario.fmb xml_output/mi_formulario.xml overwrite=yes
```

## Problemas Comunes

### "ORACLE_HOME no está configurado"

```bash
export ORACLE_HOME=/opt/oracle/middleware/forms
# Ajusta la ruta según tu instalación
```

### "frmf2xml: command not found"

```bash
export PATH=$ORACLE_HOME/bin:$PATH
```

### "FRM-18108: Failed to load objects"

Configura FORMS_PATH si usas librerías (.pll):

```bash
export FORMS_PATH=/ruta/a/tus/librerias
```

## Próximos Pasos

1. **Versionado**: Agrega los archivos XML a Git
   ```bash
   git add xml_output/
   git commit -m "Convertir formularios a XML"
   ```

2. **Análisis**: Examina la estructura del XML generado

3. **Migración**: Usa los XML como base para migración a otras tecnologías

## Ayuda Adicional

- Ver ayuda del script: `./convert_fmb_to_xml.sh --help`
- Consultar documentación completa: `README.md`
- Verificar configuración: `./verify_setup.sh`

## Ejemplo Completo

```bash
# 1. Verificar setup
./verify_setup.sh

# 2. Crear estructura
mkdir -p forms xml_output

# 3. Copiar archivos .fmb a forms/
cp /ruta/origen/*.fmb forms/

# 4. Convertir todos
./convert_fmb_to_xml.sh -d forms -o xml_output

# 5. Verificar
ls -lh xml_output/

# 6. Versionar
git add xml_output/
git commit -m "Añadir XMLs de formularios Oracle"
```

¡Listo! Tus formularios ahora están en formato XML.
