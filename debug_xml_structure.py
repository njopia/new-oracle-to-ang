#!/usr/bin/env python3
"""
Script de diagnóstico para inspeccionar estructura XML de Oracle Forms
"""

from lxml import etree
from pathlib import Path
import sys

def inspect_xml(xml_file):
    """Inspecciona la estructura de un archivo XML"""
    print(f"\n{'='*80}")
    print(f"Inspeccionando: {xml_file}")
    print(f"{'='*80}\n")

    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()

        # Información del root
        print(f"Root tag: {root.tag}")
        print(f"Root attributes: {dict(root.attrib)}")
        print(f"Namespace map: {root.nsmap}")
        print(f"\n{'='*80}")
        print("Estructura del XML (primeros 3 niveles):")
        print(f"{'='*80}\n")

        # Mostrar estructura
        def show_structure(element, level=0, max_level=3):
            if level > max_level:
                return

            indent = "  " * level
            count = len(list(element))
            attrs = ", ".join([f"{k}='{v}'" for k, v in element.attrib.items()][:2])
            attrs_str = f" [{attrs}...]" if attrs else ""

            print(f"{indent}<{element.tag}>{attrs_str}  (hijos: {count})")

            # Mostrar solo los primeros 5 hijos de cada tipo
            children_by_tag = {}
            for child in element:
                tag = child.tag
                if tag not in children_by_tag:
                    children_by_tag[tag] = []
                children_by_tag[tag].append(child)

            for tag, children in children_by_tag.items():
                if len(children) <= 3:
                    for child in children:
                        show_structure(child, level + 1, max_level)
                else:
                    show_structure(children[0], level + 1, max_level)
                    print(f"  {indent}... (y {len(children)-1} más <{tag}>)")

        show_structure(root)

        # Buscar elementos específicos
        print(f"\n{'='*80}")
        print("Búsqueda de elementos clave:")
        print(f"{'='*80}\n")

        search_elements = ['Block', 'Item', 'Trigger', 'LOV', 'Canvas', 'Window', 'ProgramUnit']

        for elem_name in search_elements:
            # Buscar sin namespace
            found = root.xpath(f".//{elem_name}")
            print(f"{elem_name}: {len(found)} encontrados")

            if len(found) == 0:
                # Buscar con variaciones de nombre
                found_lower = root.xpath(f".//{elem_name.lower()}")
                found_upper = root.xpath(f".//{elem_name.upper()}")
                print(f"  - {elem_name.lower()}: {len(found_lower)}")
                print(f"  - {elem_name.upper()}: {len(found_upper)}")

        # Contar todos los elementos únicos
        print(f"\n{'='*80}")
        print("Todos los elementos únicos en el XML:")
        print(f"{'='*80}\n")

        all_tags = set()
        for elem in root.iter():
            all_tags.add(elem.tag)

        for tag in sorted(all_tags)[:30]:  # Primeros 30
            count = len(root.xpath(f".//{tag}"))
            print(f"  {tag}: {count}")

        if len(all_tags) > 30:
            print(f"  ... y {len(all_tags) - 30} más")

        print(f"\nTotal de tipos de elementos: {len(all_tags)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Buscar XMLs en output/
        output_dir = Path("output")
        if output_dir.exists():
            xml_files = list(output_dir.glob("*.xml"))
            if xml_files:
                print(f"Encontrados {len(xml_files)} archivos XML en output/")
                for xml_file in xml_files[:3]:  # Inspeccionar primeros 3
                    inspect_xml(str(xml_file))
            else:
                print("No se encontraron archivos XML en output/")
                print("Uso: python debug_xml_structure.py <archivo.xml>")
        else:
            print("No existe el directorio output/")
            print("Uso: python debug_xml_structure.py <archivo.xml>")
    else:
        inspect_xml(sys.argv[1])
