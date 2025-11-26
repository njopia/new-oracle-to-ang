# Directorio de Formularios (.fmb)

Coloca aquí tus archivos Oracle Forms binarios (.fmb) que deseas convertir a XML.

## Estructura recomendada

```
forms/
├── modulo1/
│   ├── formulario1.fmb
│   └── formulario2.fmb
├── modulo2/
│   ├── formulario3.fmb
│   └── formulario4.fmb
└── formulario_principal.fmb
```

## Cómo usar

1. **Copiar archivos aquí**:
   ```bash
   cp /ruta/origen/*.fmb ./forms/
   ```

2. **Convertir todos los formularios**:
   ```bash
   ../convert_fmb_to_xml.sh -d . -o ../xml_output
   ```

## Nota sobre .gitignore

Los archivos .fmb están excluidos del control de versiones porque son binarios y no se pueden comparar eficientemente en Git. Solo los archivos XML se versionarán.

Si necesitas versionar los .fmb originales, considera usar Git LFS o mantenerlos en un sistema de almacenamiento separado.
