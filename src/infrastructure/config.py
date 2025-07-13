"""Configuración centralizada para la aplicación."""

import os
from enum import Enum
from typing import Optional

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Environment(str, Enum):
    """Entornos de ejecución."""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Config:
    """Configuración de la aplicación."""
    
    # Entorno
    ENV: Environment = Environment(os.getenv("ENV", "development"))
    DEBUG: bool = ENV != Environment.PRODUCTION
    
    # API
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # API de DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
    
    # Mock
    # Forzamos el uso de la API real si USE_MOCK=false en el .env
    USE_MOCK: bool = False if os.getenv("USE_MOCK", "").lower() == "false" else (ENV != Environment.PRODUCTION)
