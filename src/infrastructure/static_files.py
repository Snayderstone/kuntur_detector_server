"""Módulo para servir los archivos estáticos de la interfaz de usuario."""

import os
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI


def setup_static_files(app: FastAPI) -> None:
    """Configura los archivos estáticos para la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    # Obtener la ruta absoluta al directorio ui
    ui_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ui")
    
    # Montar los archivos estáticos
    if os.path.exists(ui_directory):
        app.mount("/ui", StaticFiles(directory=ui_directory, html=True), name="ui")
