"""Modelos de dominio para la detección de amenazas."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ThreatType(str, Enum):
    """Tipos de amenaza detectados."""
    
    EXTORSION = "extorsión"
    ROBO = "robo"
    SECUESTRO = "secuestro"
    NINGUNA = "ninguna"


class ThreatAnalysis(BaseModel):
    """Resultado del análisis de una amenaza."""
    
    keyword: str = Field(..., description="Palabra o frase clave detectada")
    threat_type: ThreatType = Field(..., description="Tipo de amenaza detectada")
    is_threat: str = Field(..., description="Indicador de si es una amenaza (SI/NO)")
    justification: str = Field("", description="Explicación de por qué se considera una amenaza")
