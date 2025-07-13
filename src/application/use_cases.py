"""Caso de uso para analizar texto y detectar amenazas."""

from src.domain.models import ThreatAnalysis
from src.domain.ports import ThreatDetectorPort


class AnalyzeTextUseCase:
    """Caso de uso para analizar texto y detectar amenazas."""
    
    def __init__(self, threat_detector: ThreatDetectorPort):
        """Inicializa el caso de uso.
        
        Args:
            threat_detector: Servicio de detección de amenazas
        """
        self._threat_detector = threat_detector
    
    async def execute(self, text: str) -> ThreatAnalysis:
        """Ejecuta el análisis del texto.
        
        Args:
            text: El texto a analizar
            
        Returns:
            El análisis de la amenaza
        """
        return await self._threat_detector.analyze_text(text)
