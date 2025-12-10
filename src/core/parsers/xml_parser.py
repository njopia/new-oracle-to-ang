#!/usr/bin/env python3
"""
Parser avanzado para archivos XML de Oracle Forms
Extrae información estructurada para generar código Angular inteligente
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class Item:
    """Representa un item de Oracle Forms (campo de formulario)"""
    name: str
    item_type: str = ""  # TEXT_ITEM, BUTTON, CHECKBOX, etc.
    data_type: str = ""  # VARCHAR2, NUMBER, DATE, etc.
    max_length: int = 0
    required: bool = False
    canvas: str = ""
    x_position: int = 0
    y_position: int = 0
    width: int = 0
    height: int = 0
    prompt: str = ""
    tooltip: str = ""
    default_value: str = ""
    enabled: bool = True
    visible: bool = True
    lov_name: str = ""  # List of Values asociada
    validation_trigger: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Trigger:
    """Representa un trigger de Oracle Forms"""
    name: str
    trigger_type: str = ""  # WHEN-NEW-FORM-INSTANCE, WHEN-BUTTON-PRESSED, etc.
    code: str = ""
    scope: str = ""  # FORM, BLOCK, ITEM
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LOV:
    """Representa un List of Values"""
    name: str
    record_group: str = ""
    title: str = ""
    width: int = 0
    height: int = 0
    columns: List[str] = field(default_factory=list)
    query: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Block:
    """Representa un bloque de Oracle Forms (agrupación de items)"""
    name: str
    items: List[Item] = field(default_factory=list)
    triggers: List[Trigger] = field(default_factory=list)
    query_data_source: str = ""  # Tabla o vista
    where_clause: str = ""
    order_by_clause: str = ""
    single_record: bool = False
    insert_allowed: bool = True
    update_allowed: bool = True
    delete_allowed: bool = True
    query_allowed: bool = True
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Canvas:
    """Representa un canvas (pantalla/ventana)"""
    name: str
    canvas_type: str = ""  # CONTENT, STACKED, TAB
    width: int = 0
    height: int = 0
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Window:
    """Representa una ventana"""
    name: str
    title: str = ""
    width: int = 0
    height: int = 0
    x_position: int = 0
    y_position: int = 0
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgramUnit:
    """Representa una unidad de programa (función/procedimiento PL/SQL)"""
    name: str
    unit_type: str = ""  # PROCEDURE, FUNCTION, PACKAGE
    code: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormStructure:
    """Estructura completa de un formulario Oracle Forms"""
    name: str
    blocks: List[Block] = field(default_factory=list)
    triggers: List[Trigger] = field(default_factory=list)
    lovs: List[LOV] = field(default_factory=list)
    canvases: List[Canvas] = field(default_factory=list)
    windows: List[Window] = field(default_factory=list)
    program_units: List[ProgramUnit] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def get_block(self, name: str) -> Optional[Block]:
        """Obtiene un bloque por nombre"""
        for block in self.blocks:
            if block.name == name:
                return block
        return None

    def get_all_items(self) -> List[Item]:
        """Obtiene todos los items de todos los bloques"""
        all_items = []
        for block in self.blocks:
            all_items.extend(block.items)
        return all_items

    def get_complexity_score(self) -> int:
        """Calcula un score de complejidad del formulario"""
        score = 0
        score += len(self.blocks) * 10
        score += sum(len(block.items) for block in self.blocks) * 5
        score += len(self.triggers) * 15
        score += len(self.lovs) * 10
        score += len(self.program_units) * 20
        return score


class OracleFormsParser:
    """Parser para archivos XML de Oracle Forms"""

    def __init__(self):
        self.current_file: Optional[str] = None

    def parse_file(self, xml_file: str) -> FormStructure:
        """
        Parsea un archivo XML de Oracle Forms

        Args:
            xml_file: Ruta al archivo XML

        Returns:
            Estructura del formulario parseada
        """
        self.current_file = xml_file
        form_name = Path(xml_file).stem

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Crear estructura del formulario
            form = FormStructure(name=form_name)

            # Parsear diferentes secciones
            self._parse_blocks(root, form)
            self._parse_triggers(root, form)
            self._parse_lovs(root, form)
            self._parse_canvases(root, form)
            self._parse_windows(root, form)
            self._parse_program_units(root, form)

            return form

        except Exception as e:
            # Si falla el parseo, retornar estructura mínima
            return FormStructure(
                name=form_name,
                properties={'parse_error': str(e)}
            )

    def _parse_blocks(self, root: ET.Element, form: FormStructure):
        """Parsea los bloques del formulario"""
        # Buscar bloques en diferentes posibles ubicaciones del XML
        block_paths = [
            './/Block',
            './/BLOCK',
            './/*[@ObjectType="Block"]',
        ]

        for path in block_paths:
            for block_elem in root.findall(path):
                block = self._parse_block(block_elem)
                if block:
                    form.blocks.append(block)

    def _parse_block(self, elem: ET.Element) -> Optional[Block]:
        """Parsea un elemento Block"""
        name = self._get_text(elem, 'Name', elem.get('Name', 'UNNAMED_BLOCK'))

        block = Block(
            name=name,
            query_data_source=self._get_text(elem, 'QueryDataSourceName'),
            where_clause=self._get_text(elem, 'WhereClause'),
            order_by_clause=self._get_text(elem, 'OrderByClause'),
            single_record=self._get_bool(elem, 'SingleRecord'),
            insert_allowed=self._get_bool(elem, 'InsertAllowed', True),
            update_allowed=self._get_bool(elem, 'UpdateAllowed', True),
            delete_allowed=self._get_bool(elem, 'DeleteAllowed', True),
            query_allowed=self._get_bool(elem, 'QueryAllowed', True)
        )

        # Parsear items del bloque
        for item_elem in elem.findall('.//Item'):
            item = self._parse_item(item_elem)
            if item:
                block.items.append(item)

        # Parsear triggers del bloque
        for trigger_elem in elem.findall('.//Trigger'):
            trigger = self._parse_trigger(trigger_elem)
            if trigger:
                trigger.scope = 'BLOCK'
                block.triggers.append(trigger)

        return block

    def _parse_item(self, elem: ET.Element) -> Optional[Item]:
        """Parsea un elemento Item"""
        name = self._get_text(elem, 'Name', elem.get('Name', 'UNNAMED_ITEM'))

        item = Item(
            name=name,
            item_type=self._get_text(elem, 'ItemType', 'TEXT_ITEM'),
            data_type=self._get_text(elem, 'DataType', 'VARCHAR2'),
            max_length=self._get_int(elem, 'MaximumLength', 0),
            required=self._get_bool(elem, 'Required'),
            canvas=self._get_text(elem, 'CanvasName'),
            x_position=self._get_int(elem, 'XPosition', 0),
            y_position=self._get_int(elem, 'YPosition', 0),
            width=self._get_int(elem, 'Width', 100),
            height=self._get_int(elem, 'Height', 20),
            prompt=self._get_text(elem, 'PromptText'),
            tooltip=self._get_text(elem, 'Tooltip'),
            default_value=self._get_text(elem, 'InitialValue'),
            enabled=self._get_bool(elem, 'Enabled', True),
            visible=self._get_bool(elem, 'Visible', True),
            lov_name=self._get_text(elem, 'ListOfValuesName')
        )

        return item

    def _parse_triggers(self, root: ET.Element, form: FormStructure):
        """Parsea los triggers a nivel formulario"""
        for trigger_elem in root.findall('.//FormLevelTrigger'):
            trigger = self._parse_trigger(trigger_elem)
            if trigger:
                trigger.scope = 'FORM'
                form.triggers.append(trigger)

    def _parse_trigger(self, elem: ET.Element) -> Optional[Trigger]:
        """Parsea un elemento Trigger"""
        name = self._get_text(elem, 'Name', elem.get('Name', 'UNNAMED_TRIGGER'))

        trigger = Trigger(
            name=name,
            trigger_type=self._get_text(elem, 'TriggerType'),
            code=self._get_text(elem, 'TriggerText')
        )

        return trigger

    def _parse_lovs(self, root: ET.Element, form: FormStructure):
        """Parsea los LOVs (List of Values)"""
        for lov_elem in root.findall('.//LOV'):
            lov = self._parse_lov(lov_elem)
            if lov:
                form.lovs.append(lov)

    def _parse_lov(self, elem: ET.Element) -> Optional[LOV]:
        """Parsea un elemento LOV"""
        name = self._get_text(elem, 'Name', elem.get('Name', 'UNNAMED_LOV'))

        lov = LOV(
            name=name,
            record_group=self._get_text(elem, 'RecordGroup'),
            title=self._get_text(elem, 'Title'),
            width=self._get_int(elem, 'Width', 300),
            height=self._get_int(elem, 'Height', 200)
        )

        # Parsear columnas
        for col_elem in elem.findall('.//ColumnMapping'):
            col_name = self._get_text(col_elem, 'Name')
            if col_name:
                lov.columns.append(col_name)

        return lov

    def _parse_canvases(self, root: ET.Element, form: FormStructure):
        """Parsea los canvas"""
        for canvas_elem in root.findall('.//Canvas'):
            canvas = Canvas(
                name=self._get_text(canvas_elem, 'Name', 'UNNAMED_CANVAS'),
                canvas_type=self._get_text(canvas_elem, 'CanvasType', 'CONTENT'),
                width=self._get_int(canvas_elem, 'Width', 800),
                height=self._get_int(canvas_elem, 'Height', 600)
            )
            form.canvases.append(canvas)

    def _parse_windows(self, root: ET.Element, form: FormStructure):
        """Parsea las ventanas"""
        for window_elem in root.findall('.//Window'):
            window = Window(
                name=self._get_text(window_elem, 'Name', 'UNNAMED_WINDOW'),
                title=self._get_text(window_elem, 'Title'),
                width=self._get_int(window_elem, 'Width', 800),
                height=self._get_int(window_elem, 'Height', 600),
                x_position=self._get_int(window_elem, 'XPosition', 0),
                y_position=self._get_int(window_elem, 'YPosition', 0)
            )
            form.windows.append(window)

    def _parse_program_units(self, root: ET.Element, form: FormStructure):
        """Parsea las unidades de programa (PL/SQL)"""
        for unit_elem in root.findall('.//ProgramUnit'):
            unit = ProgramUnit(
                name=self._get_text(unit_elem, 'Name', 'UNNAMED_UNIT'),
                unit_type=self._get_text(unit_elem, 'ProgramUnitType', 'PROCEDURE'),
                code=self._get_text(unit_elem, 'ProgramUnitText')
            )
            form.program_units.append(unit)

    # Utilidades para extraer datos del XML

    def _get_text(self, elem: ET.Element, tag: str, default: str = "") -> str:
        """Obtiene el texto de un tag hijo"""
        child = elem.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return default

    def _get_int(self, elem: ET.Element, tag: str, default: int = 0) -> int:
        """Obtiene un valor entero de un tag hijo"""
        text = self._get_text(elem, tag)
        if text:
            try:
                return int(text)
            except ValueError:
                pass
        return default

    def _get_bool(self, elem: ET.Element, tag: str, default: bool = False) -> bool:
        """Obtiene un valor booleano de un tag hijo"""
        text = self._get_text(elem, tag)
        if text:
            return text.upper() in ('TRUE', 'YES', '1', 'Y')
        return default
