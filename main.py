"""Punto de entrada principal del servidor de detección de amenazas Kuntur."""

import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from src.infrastructure.api import ThreatDetectionAPI
from src.infrastructure.config import Config


def main():
    """Inicia el servidor de la API."""
    # Crear y obtener la instancia de la API
    api_instance = ThreatDetectionAPI()
    app = api_instance.app
    
    # Obtener la configuración del servidor
    host = Config.HOST
    port = Config.PORT
    
    print(f"Iniciando servidor Kuntur Detector en http://{host}:{port}")
    print(f"Modo: {'Simulado' if Config.USE_MOCK else 'Real'}")
    print(f"Ambiente: {Config.ENV}")
    print(f"UI disponible en: http://{host}:{port}/ui/")
    print(f"Documentación API: http://{host}:{port}/docs")
    
    # Iniciar el servidor
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
