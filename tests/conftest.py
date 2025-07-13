"""Configuración para pytest."""

import os
import sys

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
