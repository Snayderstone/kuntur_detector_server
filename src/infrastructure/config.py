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
    USE_MOCK: bool = os.getenv("USE_MOCK", "false").lower() == "true"
    
    # Sistema de caché
    USE_CACHE: bool = os.getenv("USE_CACHE", "true").lower() == "true"
    CACHE_TTL_HOURS: int = int(os.getenv("CACHE_TTL_HOURS", "24"))
