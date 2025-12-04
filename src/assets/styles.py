#!/usr/bin/env python3
"""
Estilos y colores de la aplicación
Inspirados en Material Design y la imagen de referencia
"""

# Paleta de colores principal (basada en la imagen)
COLORS = {
    # Azules principales
    'primary': '#1976D2',
    'primary_dark': '#0D47A1',
    'primary_light': '#42A5F5',
    'primary_lighter': '#64B5F6',

    # Secundarios
    'secondary': '#2196F3',
    'accent': '#03A9F4',

    # Estados
    'success': '#4CAF50',
    'success_light': '#81C784',
    'warning': '#FF9800',
    'warning_light': '#FFB74D',
    'error': '#F44336',
    'error_light': '#E57373',
    'info': '#2196F3',

    # Fondos
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F5F5F5',
    'bg_tertiary': '#FAFAFA',
    'bg_dark': '#263238',

    # Texto
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'text_disabled': '#BDBDBD',
    'text_white': '#FFFFFF',

    # Bordes y divisores
    'border': '#E0E0E0',
    'divider': '#EEEEEE',

    # Hover y estados
    'hover': '#E3F2FD',
    'selected': '#BBDEFB',
    'disabled': '#F5F5F5',

    # Stepper
    'stepper_active': '#1976D2',
    'stepper_completed': '#4CAF50',
    'stepper_pending': '#9E9E9E',
    'stepper_line': '#E0E0E0'
}

# Fuentes
FONTS = {
    'family': 'Segoe UI',
    'family_mono': 'Consolas',

    'size_tiny': 10,
    'size_small': 11,
    'size_normal': 12,
    'size_medium': 14,
    'size_large': 16,
    'size_xlarge': 18,
    'size_xxlarge': 24,
    'size_title': 28,
    'size_hero': 36,

    'weight_normal': 'normal',
    'weight_medium': 'normal',  # CustomTkinter no siempre soporta 'medium'
    'weight_bold': 'bold'
}

# Espaciado (optimizado para maximizar contenido)
SPACING = {
    'xs': 3,
    'sm': 6,
    'md': 10,
    'lg': 14,
    'xl': 18,
    'xxl': 24
}

# Bordes redondeados
CORNER_RADIUS = {
    'none': 0,
    'sm': 4,
    'md': 6,
    'lg': 10,
    'xl': 15,
    'round': 50
}

# Tamaños de elementos (optimizados)
SIZES = {
    'button_height': 32,
    'button_width': 110,
    'input_height': 34,
    'stepper_circle': 36,
    'stepper_line_height': 2,
    'icon_sm': 16,
    'icon_md': 20,
    'icon_lg': 28
}

# Opacidades
OPACITY = {
    'disabled': 0.5,
    'hover': 0.8,
    'overlay': 0.3
}

# Animaciones (duraciones en ms)
ANIMATIONS = {
    'fast': 150,
    'normal': 250,
    'slow': 350
}

# Dimensiones de ventana
WINDOW = {
    'min_width': 1000,
    'min_height': 700,
    'default_width': 1200,
    'default_height': 800
}


def get_color(key: str, default: str = '#000000') -> str:
    """
    Obtiene un color de la paleta

    Args:
        key: Clave del color
        default: Color por defecto si no existe

    Returns:
        Código hexadecimal del color
    """
    return COLORS.get(key, default)


def get_font(size: str = 'normal', weight: str = 'normal') -> tuple:
    """
    Obtiene una configuración de fuente

    Args:
        size: Tamaño de fuente (tiny, small, normal, medium, large, etc.)
        weight: Peso de fuente (normal, medium, bold)

    Returns:
        Tupla (familia, tamaño, peso)
    """
    font_family = FONTS['family']
    font_size = FONTS.get(f'size_{size}', FONTS['size_normal'])
    font_weight = FONTS.get(f'weight_{weight}', FONTS['weight_normal'])

    return (font_family, font_size, font_weight)


def get_font_dict(size: str = 'normal', weight: str = 'normal') -> dict:
    """
    Obtiene una configuración de fuente como diccionario

    Args:
        size: Tamaño de fuente
        weight: Peso de fuente

    Returns:
        Diccionario con configuración de fuente
    """
    font_family = FONTS['family']
    font_size = FONTS.get(f'size_{size}', FONTS['size_normal'])
    font_weight = FONTS.get(f'weight_{weight}', FONTS['weight_normal'])

    return {
        'family': font_family,
        'size': font_size,
        'weight': font_weight
    }
