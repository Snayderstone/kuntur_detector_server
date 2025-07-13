"""Tests para asegurarse de que la estructura del proyecto es correcta."""

import pytest
import os


def test_project_structure():
    """Comprueba que la estructura del proyecto es correcta."""
    assert os.path.exists("src"), "Debe existir el directorio src"
    assert os.path.exists("src/domain"), "Debe existir el directorio domain"
    assert os.path.exists("src/application"), "Debe existir el directorio application"
    assert os.path.exists("src/infrastructure"), "Debe existir el directorio infrastructure"
    
    # Comprobar archivos de dominio
    assert os.path.exists("src/domain/models.py"), "Debe existir el archivo de modelos"
    assert os.path.exists("src/domain/ports.py"), "Debe existir el archivo de puertos"
    
    # Comprobar archivos de aplicación
    assert os.path.exists("src/application/use_cases.py"), "Debe existir el archivo de casos de uso"
    
    # Comprobar archivos de infraestructura
    assert os.path.exists("src/infrastructure/api.py"), "Debe existir el archivo de API"
    assert os.path.exists("src/infrastructure/threat_detector.py"), "Debe existir el archivo del detector de amenazas"
