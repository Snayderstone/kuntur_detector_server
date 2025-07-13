"""Tests para los modelos de dominio."""

import pytest
from src.domain.models import ThreatType, ThreatAnalysis


def test_threat_type_enum():
    """Test para comprobar que los tipos de amenazas están correctamente definidos."""
    assert ThreatType.EXTORSION == "extorsión"
    assert ThreatType.ROBO == "robo"
    assert ThreatType.SECUESTRO == "secuestro"
    assert ThreatType.NINGUNA == "ninguna"


def test_threat_analysis_model():
    """Test para comprobar que el modelo de análisis de amenazas se puede crear correctamente."""
    # Crear un análisis de amenaza válido
    threat = ThreatAnalysis(
        keyword="vacunas", 
        threat_type=ThreatType.EXTORSION, 
        is_threat="SI"
    )
    
    # Comprobar que los campos son correctos
    assert threat.keyword == "vacunas"
    assert threat.threat_type == ThreatType.EXTORSION
    assert threat.is_threat == "SI"
    
    # Crear un análisis sin amenaza
    no_threat = ThreatAnalysis(
        keyword="ninguna", 
        threat_type=ThreatType.NINGUNA, 
        is_threat="NO"
    )
    
    assert no_threat.keyword == "ninguna"
    assert no_threat.threat_type == ThreatType.NINGUNA
    assert no_threat.is_threat == "NO"
