# Oracle Forms to Angular Migrator v3.0

🚀 Herramienta profesional para migrar aplicaciones Oracle Forms a Angular con análisis completo y generación de código.

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6%2B-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías](#tecnologías)
- [Fases de Migración](#fases-de-migración)
- [Capturas de Pantalla](#capturas-de-pantalla)
- [Contribuir](#contribuir)

## ✨ Características

### Fase 1 (Actual - Steps 1-3)

- ✅ **Verificación de Prerequisitos**: Detección automática de Node.js, npm, Java JDK, Oracle Forms, Python
- ✅ **Carga de Archivos**: Interfaz drag & drop para archivos `.fmb` múltiples
- ✅ **Conversión FMB a XML**: Utiliza `frmf2xml.bat` de Oracle Forms
- ✅ **Análisis Profundo**: Extracción de métricas (bloques, items, triggers, LOVs, etc.)
- ✅ **Reportes HTML**: Generación de reportes interactivos con gráficos Chart.js
- ✅ **Multiidioma**: Soporte para Español e Inglés con cambio en runtime
- ✅ **Interfaz Moderna**: GUI con CustomTkinter tipo Material Design

### Fase 2 (Futuro - Steps 4-6)

- ⏳ **Configuración**: Mapeo de componentes Oracle Forms a Angular
- ⏳ **Generación de Código**: Generación automática de componentes Angular
- ⏳ **Exportación**: Proyecto Angular completo listo para usar

## 📦 Requisitos

### Obligatorios

- **Python 3.6+**
- **Oracle Forms** (con `frmf2xml.bat`)
- **Java JDK 1.8+**
- **ORACLE_HOME** configurado

### Opcionales (para proyectos Angular)

- **Node.js v24.9+**
- **npm**

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/njopia/oracle-to-angular.git
cd oracle-to-angular
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Asegúrate de que `ORACLE_HOME` esté configurado:

```bash
# Windows
set ORACLE_HOME=C:\\Oracle\\Middleware\\Oracle_Home
set PATH=%ORACLE_HOME%\\bin;%PATH%

# Linux/Mac
export ORACLE_HOME=/opt/oracle/middleware/oracle_home
export PATH=$ORACLE_HOME/bin:$PATH
```

## 💻 Uso

### Ejecución

```bash
python main.py
```

### Flujo de Trabajo

1. **Step 1 - Prerequisitos**
   - Haz clic en "Verificar Prerequisitos"
   - Confirma que todas las herramientas estén instaladas
   - Haz clic en "Siguiente"

2. **Step 2 - Carga de Archivos**
   - Arrastra archivos `.fmb` o usa "Agregar Archivos"
   - Puedes seleccionar múltiples archivos
   - Haz clic en "Siguiente"

3. **Step 3 - Análisis**
   - Haz clic en "Iniciar Análisis"
   - Espera a que complete la conversión y análisis
   - Haz clic en "Abrir Reporte" para ver los resultados

### Cambiar Idioma

Usa el selector en la esquina superior derecha para cambiar entre Español e Inglés en cualquier momento.

## 📁 Estructura del Proyecto

```
oracle-to-angular/
├── src/
│   ├── assets/
│   │   ├── styles.py              # Colores, fuentes, estilos
│   │   └── templates/             # Templates HTML
│   ├── core/
│   │   ├── verificator.py         # Verificación de prerequisitos
│   │   ├── converter.py           # Conversión FMB a XML
│   │   ├── analyzer.py            # Análisis de XML
│   │   └── report_generator.py   # Generación de reportes
│   ├── gui/
│   │   ├── main_window.py         # Ventana principal
│   │   ├── stepper.py             # Widget stepper
│   │   ├── step_prerequisites.py  # Step 1
│   │   ├── step_file.py           # Step 2
│   │   └── step_analysis.py       # Step 3
│   ├── locales/
│   │   ├── es.json                # Traducciones español
│   │   └── en.json                # Traducciones inglés
│   └── utils/
│       ├── config.py              # Gestión de configuración
│       ├── i18n.py                # Internacionalización
│       └── logger.py              # Sistema de logging
├── output/                         # XMLs y reportes generados
├── temp/                           # Archivos temporales
├── logs/                           # Logs de la aplicación
├── config.json                     # Configuración de usuario
├── requirements.txt                # Dependencias Python
├── main.py                         # Punto de entrada
└── README.md                       # Este archivo
```

## 🛠️ Tecnologías

- **Python 3.6+**
- **CustomTkinter** - GUI moderna
- **lxml** - Parseo de XML
- **Jinja2** - Templates HTML
- **Chart.js** - Gráficos interactivos
- **Oracle Forms Tools** - frmf2xml.bat

## 📊 Fases de Migración

### ✅ Fase 1: Análisis (Actual)

- Verificación de prerequisitos
- Carga de archivos .fmb
- Conversión a XML
- Análisis de estructura
- Generación de reportes

### ⏳ Fase 2: Configuración (Próximamente)

- Mapeo de componentes
- Configuración de reglas de migración
- Personalización de templates

### ⏳ Fase 3: Generación (Futuro)

- Generación de componentes Angular
- Generación de servicios
- Generación de modelos
- Exportación de proyecto completo

## 📷 Capturas de Pantalla

*(Aquí irían screenshots de la aplicación)*

### Step 1: Prerequisitos
![Step 1](docs/screenshots/step1.png)

### Step 2: Carga de Archivos
![Step 2](docs/screenshots/step2.png)

### Step 3: Análisis
![Step 3](docs/screenshots/step3.png)

### Reporte HTML
![Report](docs/screenshots/report.png)

## 🐛 Solución de Problemas

### Error: "ORACLE_HOME no está configurado"

```bash
set ORACLE_HOME=C:\\ruta\\a\\oracle
```

### Error: "frmf2xml.bat not found"

Verifica que `frmf2xml.bat` esté en:
- `%ORACLE_HOME%\\forms\\templates\\scripts\\frmf2xml.bat`
- O en `%ORACLE_HOME%\\bin\\frmf2xml.bat`

### Error: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

## 📝 Configuración Avanzada

Puedes editar `config.json` para personalizar:

```json
{
  "paths": {
    "oracle_home": "C:\\\\Oracle\\\\Middleware\\\\Oracle_Home",
    "output_directory": "./output"
  },
  "ui": {
    "theme": "blue",
    "appearance_mode": "light"
  },
  "conversion": {
    "timeout_seconds": 300
  }
}
```

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 👤 Autor

**njopia**

- GitHub: [@njopia](https://github.com/njopia)

## 🙏 Agradecimientos

- Oracle Forms Documentation
- CustomTkinter Community
- Chart.js Team

## 📮 Contacto

Si tienes preguntas o sugerencias, abre un issue en GitHub.

---

⭐️ Si este proyecto te fue útil, dale una estrella en GitHub!
