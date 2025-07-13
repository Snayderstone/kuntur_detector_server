"""Interfaces para los servicios de detección de amenazas."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.models import ThreatAnalysis


class ThreatDetectorPort(ABC):
    """Interfaz para la detección de amenazas."""
    
    @abstractmethod
    async def analyze_text(self, text: str) -> ThreatAnalysis:
        """Analiza un texto y determina si contiene amenazas.
        
        Args:
            text: El texto a analizar
            
        Returns:
            El análisis de la amenaza
        """
        pass
