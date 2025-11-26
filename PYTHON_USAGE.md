# Guía de Uso de Scripts Python

Todos los scripts han sido migrados a Python para mejor portabilidad y mantenibilidad.

## 📋 Requisitos

```bash
# Python 3.6+
python3 --version

# Oracle Forms instalado
echo $ORACLE_HOME

# Java instalado (opcional pero recomendado)
java -version
```

## 🚀 Scripts Disponibles

### 1. verify_setup.py - Verificación de Configuración

Verifica que todo esté configurado correctamente.

```bash
python3 verify_setup.py
```

**Salida de ejemplo:**
```
=== Verificación de Configuración de Oracle Forms ===

[1/6] Verificando ORACLE_HOME...
✓ ORACLE_HOME: /opt/oracle/middleware/forms

[2/6] Verificando frmf2xml...
✓ frmf2xml encontrado: /opt/oracle/middleware/forms/bin/frmf2xml

[3/6] Verificando JAVA_HOME...
✓ JAVA_HOME: /usr/lib/jvm/java-8-openjdk-amd64

[4/6] Verificando Java...
✓ Java encontrado: openjdk version "1.8.0_352"

[5/6] Verificando LD_LIBRARY_PATH...
✓ LD_LIBRARY_PATH incluye ORACLE_HOME

[6/6] Verificando PATH...
✓ PATH incluye $ORACLE_HOME/bin

=== RESUMEN ===
✓ ¡Todo está configurado correctamente!
```

---

### 2. setup_environment.py - Asistente de Configuración

Configura las variables de entorno de forma interactiva.

```bash
python3 setup_environment.py
```

**Características:**
- 🔍 Busca automáticamente instalaciones de Oracle Forms y Java
- 📝 Sugiere rutas encontradas
- ✅ Valida las rutas antes de aceptarlas
- 💾 Puede crear un archivo `.env` con la configuración
- 🔧 Opción de verificar la configuración al finalizar

**Flujo de uso:**
```bash
$ python3 setup_environment.py

=== Configuración de Variables de Entorno para Oracle Forms ===

🔍 Buscando instalaciones de Oracle Forms y Java...

Configurando ORACLE_HOME:

Rutas encontradas:
  1. /opt/oracle/middleware/forms
  2. /u01/app/oracle/product/12.2.1/forms
  0. Ingresar ruta manualmente

Selecciona una opción [1-2, 0 para manual]: 1
✓ ORACLE_HOME configurado: /opt/oracle/middleware/forms

...

¿Deseas crear un archivo .env local con estas variables? (s/n): s
✓ Archivo creado: .env
Para usar: source .env
```

---

### 3. convert_fmb_to_xml.py - Conversión FMB a XML

Script principal para convertir archivos Oracle Forms a XML.

#### Convertir un archivo único

```bash
python3 convert_fmb_to_xml.py -f formulario.fmb
```

#### Convertir un directorio completo

```bash
python3 convert_fmb_to_xml.py -d forms -o xml_output
```

#### Opciones disponibles

```bash
python3 convert_fmb_to_xml.py --help
```

```
usage: convert_fmb_to_xml.py [-h] [-f FILE] [-d DIRECTORY] [-o OUTPUT]

Convierte archivos Oracle Forms (.fmb) a XML

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Convertir un archivo específico
  -d DIRECTORY, --directory DIRECTORY
                        Convertir todos los .fmb en un directorio
  -o OUTPUT, --output OUTPUT
                        Directorio de salida (default: ./output)

Ejemplos:
  convert_fmb_to_xml.py -f mi_formulario.fmb
  convert_fmb_to_xml.py -d ./forms -o ./xml_output
  convert_fmb_to_xml.py --file forms/ejemplo.fmb --output salida
```

#### Salida de ejemplo

```bash
$ python3 convert_fmb_to_xml.py -d forms -o xml_output

✓ ORACLE_HOME encontrado: /opt/oracle/middleware/forms
✓ Directorio de salida: xml_output

Buscando archivos .fmb en: forms
Encontrados 3 archivo(s) .fmb

Convirtiendo: forms/empleados.fmb
✓ Éxito: xml_output/empleados.xml

Convirtiendo: forms/clientes.fmb
✓ Éxito: xml_output/clientes.xml

Convirtiendo: forms/ventas.fmb
✓ Éxito: xml_output/ventas.xml

=== RESUMEN ===
Conversiones exitosas: 3
Errores: 0
```

---

## 🎯 Flujo de Trabajo Recomendado

### Primera vez (configuración inicial)

```bash
# 1. Verificar Python
python3 --version

# 2. Configurar variables de entorno
python3 setup_environment.py

# 3. Verificar que todo esté bien
python3 verify_setup.py

# 4. Cargar las variables (si creaste .env)
source .env
```

### Uso diario (después de la configuración)

```bash
# 1. Asegurar que las variables están cargadas
source .env  # o source ~/.bashrc

# 2. Copiar archivos .fmb a convertir
cp /ruta/original/*.fmb forms/

# 3. Convertir
python3 convert_fmb_to_xml.py -d forms -o xml_output

# 4. Verificar resultados
ls -lh xml_output/

# 5. Versionar en Git
git add xml_output/
git commit -m "Actualizar XMLs de formularios"
```

---

## 🛠️ Características de los Scripts Python

### ✨ Ventajas sobre los scripts Bash

1. **Multiplataforma**: Funciona en Linux, macOS y Windows
2. **Mejor manejo de errores**: Excepciones claras y mensajes informativos
3. **Salida coloreada**: Fácil de identificar éxitos, errores y advertencias
4. **Validaciones**: Verifica rutas y archivos antes de ejecutar
5. **Interactividad**: Asistente de configuración con sugerencias automáticas
6. **Código limpio**: Type hints, documentación y estructura clara

### 🎨 Códigos de color

- 🟢 **Verde**: Éxito
- 🔴 **Rojo**: Error
- 🟡 **Amarillo**: Advertencia
- 🔵 **Azul**: Información

### ⚡ Rendimiento

- Conversión en paralelo (usa subprocess con timeout)
- Búsqueda recursiva eficiente de archivos .fmb
- Caché de validaciones para evitar repetir verificaciones

---

## 📝 Ejemplos Avanzados

### Convertir con estructura de directorios

```bash
# Mantiene la estructura de subdirectorios
python3 convert_fmb_to_xml.py -d forms -o xml_output
```

Si tienes:
```
forms/
├── modulo1/
│   └── form1.fmb
└── modulo2/
    └── form2.fmb
```

Obtienes (todos en el mismo nivel de salida):
```
xml_output/
├── form1.xml
└── form2.xml
```

### Script de conversión automática

Crear `convert_all.sh`:
```bash
#!/bin/bash
# Convertir todos los formularios y hacer commit

# Cargar variables
source .env

# Convertir
python3 convert_fmb_to_xml.py -d forms -o xml_output

# Si fue exitoso, hacer commit
if [ $? -eq 0 ]; then
    git add xml_output/
    git commit -m "Actualizar XMLs - $(date +%Y-%m-%d)"
    echo "✓ Conversión y commit completados"
else
    echo "✗ Error en la conversión"
    exit 1
fi
```

### Integración con CI/CD

```yaml
# .github/workflows/convert-forms.yml
name: Convert Oracle Forms

on:
  push:
    paths:
      - 'forms/**'

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Oracle environment
        run: |
          # Configurar ORACLE_HOME, etc.

      - name: Convert forms to XML
        run: python3 convert_fmb_to_xml.py -d forms -o xml_output

      - name: Commit changes
        run: |
          git add xml_output/
          git commit -m "Auto-convert forms to XML"
          git push
```

---

## 🐛 Solución de Problemas

### ModuleNotFoundError

```bash
# Los scripts usan solo librerías estándar de Python
# Si tienes este error, verifica tu instalación de Python
python3 -m pip install --upgrade pip
```

### Permission denied

```bash
# Dar permisos de ejecución
chmod +x *.py
```

### Encoding errors

Los scripts usan UTF-8 por defecto. Si tienes problemas:
```bash
export PYTHONIOENCODING=utf-8
```

---

## 📚 Recursos Adicionales

- **README.md**: Documentación completa del proyecto
- **QUICKSTART.md**: Guía rápida de inicio
- **COMMANDS.md**: Referencia de comandos útiles
- **example_config.env**: Plantilla de configuración

---

## 🔄 Migración desde Scripts Bash

Si venías usando los scripts Bash (`.sh`), simplemente reemplaza:

```bash
# Antes (Bash)
./verify_setup.sh
./setup_environment.sh
./convert_fmb_to_xml.sh -d forms -o xml_output

# Ahora (Python)
python3 verify_setup.py
python3 setup_environment.py
python3 convert_fmb_to_xml.py -d forms -o xml_output
```

Los scripts Bash originales se mantienen para compatibilidad, pero se recomienda usar las versiones Python.

---

## ✅ Checklist de Inicio Rápido

- [ ] Python 3.6+ instalado
- [ ] Oracle Forms instalado
- [ ] Ejecutar `python3 setup_environment.py`
- [ ] Ejecutar `python3 verify_setup.py`
- [ ] Copiar archivos .fmb a `forms/`
- [ ] Ejecutar `python3 convert_fmb_to_xml.py -d forms -o xml_output`
- [ ] Verificar XMLs en `xml_output/`
- [ ] Hacer commit de los XMLs a Git

¡Listo para usar! 🎉
