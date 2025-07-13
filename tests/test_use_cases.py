"""Tests para los casos de uso."""

import pytest
from unittest.mock import AsyncMock, Mock

from src.application.use_cases import AnalyzeTextUseCase
from src.domain.models import ThreatAnalysis, ThreatType
from src.domain.ports import ThreatDetectorPort


class MockThreatDetector(ThreatDetectorPort):
    """Mock del detector de amenazas para pruebas."""
    
    def __init__(self):
        self.analyze_text_mock = AsyncMock()
    
    async def analyze_text(self, text: str) -> ThreatAnalysis:
        return await self.analyze_text_mock(text)


@pytest.mark.asyncio
async def test_analyze_text_use_case():
    """Test para comprobar que el caso de uso de análisis de texto funciona correctamente."""
    # Crear el mock del detector de amenazas
    mock_detector = MockThreatDetector()
    mock_detector.analyze_text_mock.return_value = ThreatAnalysis(
        keyword="vacunas", 
        threat_type=ThreatType.EXTORSION, 
        is_threat="SI"
    )
    
    # Crear el caso de uso con el mock
    use_case = AnalyzeTextUseCase(mock_detector)
    
    # Ejecutar el caso de uso
    result = await use_case.execute("Texto de prueba")
    
    # Comprobar que el detector fue llamado correctamente
    mock_detector.analyze_text_mock.assert_called_once_with("Texto de prueba")
    
    # Comprobar que el resultado es correcto
    assert result.keyword == "vacunas"
    assert result.threat_type == ThreatType.EXTORSION
    assert result.is_threat == "SI"
