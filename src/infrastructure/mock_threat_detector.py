"""Adaptador para simulación de la API DeepSeek en entornos de desarrollo y pruebas."""

import os
import json
from typing import Dict

from src.domain.models import ThreatAnalysis, ThreatType
from src.domain.ports import ThreatDetectorPort

class MockDeepSeekThreatDetector(ThreatDetectorPort):
    """Simulación del detector de amenazas para pruebas y desarrollo."""
    
    async def analyze_text(self, text: str) -> ThreatAnalysis:
        """Analiza un texto y simula una detección de amenazas.
        
        Args:
            text: El texto a analizar
            
        Returns:
            El análisis de la amenaza simulado
        """
        text_lower = text.lower()
        
        # Patrones complejos para detectar amenazas por contexto e intención
        extorsion_patterns = [
            {"keyword": "colaboración", "context": ["banda", "pequeña", "grupo", "saluda", "lobos"]},
            {"keyword": "vacuna", "context": []},
            {"keyword": "colaborar", "context": ["evitar", "problema", "causa"]},
            {"keyword": "protección", "context": ["servicio", "ofrecer", "negocio", "seguro"]},
            {"keyword": "seguridad", "context": ["negocio", "local", "garantizar", "conversación"]},
            {"keyword": "cuota", "context": []},
            {"keyword": "aporte", "context": []},
            {"keyword": "prevenir", "context": ["problema", "accidente", "desgracia"]},
            {"keyword": "acuerdo", "context": ["llegar", "garantizar", "seguridad"]},
            {"keyword": "ofrecemos", "context": ["seguridad", "tranquilidad", "protección"]},
            {"keyword": "saluda", "context": ["banda", "grupo", "organización"]},
            {"keyword": "conversación", "context": ["importante", "negocio", "local"]},
        ]
        
        robo_patterns = [
            {"keyword": "susto", "context": []},
            {"keyword": "visita", "context": ["hacer", "realizar", "pasar"]},
            {"keyword": "conocer", "context": ["familia", "casa", "negocio", "dirección"]},
            {"keyword": "limpiar", "context": ["local", "negocio", "casa"]},
            {"keyword": "revisar", "context": ["pertenencia", "valor", "inventario"]},
            {"keyword": "pendiente", "context": ["estar", "quedar", "familia"]},
            {"keyword": "visitar", "context": ["pronto", "casa", "negocio"]},
        ]
        
        secuestro_patterns = [
            {"keyword": "vuelta", "context": ["dar", "llevar", "pasear"]},
            {"keyword": "paseo", "context": []},
            {"keyword": "conversar", "context": ["afuera", "privado", "lugar"]},
            {"keyword": "visitar", "context": ["familia", "hijo", "hija", "conocer"]},
            {"keyword": "recoger", "context": ["personal", "personalmente"]},
            {"keyword": "acompañar", "context": ["salir", "lugar"]},
        ]
        
        # Palabras clave simples (para mantener compatibilidad)
        extorsion_keywords = ["vacuna", "vacunas", "pago", "protección", "colaborar", "cuota", "seguridad", "colaboración", "banda", "aporte", "apoyo"]
        robo_keywords = ["susto", "visita", "asustar", "limpiar", "revisar", "conocer"]
        secuestro_keywords = ["vuelta", "llevar", "paseo", "desaparecer", "conversar", "afuera"]
        
        # Función para verificar si un patrón de amenaza está presente
        def check_pattern_match(text: str, patterns: list) -> dict:
            for pattern in patterns:
                keyword = pattern["keyword"]
                if keyword in text_lower:
                    # Si la palabra clave está presente
                    if not pattern["context"]:  # Si no hay contexto requerido
                        return {"matched": True, "keyword": keyword}
                    # Si hay contexto, verificar si al menos uno está presente
                    if any(ctx in text_lower for ctx in pattern["context"]):
                        return {"matched": True, "keyword": keyword, 
                                "context": next((ctx for ctx in pattern["context"] if ctx in text_lower), "")}
            # No se encontró coincidencia
            return {"matched": False}
        
        # Analizar para amenazas específicas usando patrones complejos
        try:
            # Verificar extorsión
            extorsion_match = check_pattern_match(text_lower, extorsion_patterns)
            if extorsion_match["matched"]:
                keyword = extorsion_match["keyword"]
                context = extorsion_match.get("context", "")
                justification = f"Se detectó una posible extorsión por el uso de '{keyword}'"
                if context:
                    justification += f" en contexto con '{context}'"
                return ThreatAnalysis(
                    keyword=keyword,
                    threat_type=ThreatType.EXTORSION,
                    is_threat="SI",
                    justification=justification
                )
            
            # Verificar robo
            robo_match = check_pattern_match(text_lower, robo_patterns)
            if robo_match["matched"]:
                keyword = robo_match["keyword"]
                context = robo_match.get("context", "")
                justification = f"Se detectó una posible amenaza de robo por el uso de '{keyword}'"
                if context:
                    justification += f" en contexto con '{context}'"
                return ThreatAnalysis(
                    keyword=keyword,
                    threat_type=ThreatType.ROBO,
                    is_threat="SI",
                    justification=justification
                )
            
            # Verificar secuestro
            secuestro_match = check_pattern_match(text_lower, secuestro_patterns)
            if secuestro_match["matched"]:
                keyword = secuestro_match["keyword"]
                context = secuestro_match.get("context", "")
                justification = f"Se detectó una posible amenaza de secuestro por el uso de '{keyword}'"
                if context:
                    justification += f" en contexto con '{context}'"
                return ThreatAnalysis(
                    keyword=keyword,
                    threat_type=ThreatType.SECUESTRO,
                    is_threat="SI",
                    justification=justification
                )
            
            # Verificar combinaciones contextuales (método principal)
            # Caso específico para "banda de los lobos" pidiendo "colaboración" (ejemplo del usuario)
            if ("banda" in text_lower or "grupo" in text_lower) and ("saluda" in text_lower) and ("colaboración" in text_lower or "colaborar" in text_lower):
                return ThreatAnalysis(
                    keyword="colaboración con banda",
                    threat_type=ThreatType.EXTORSION,
                    is_threat="SI",
                    justification="Se detectó una posible extorsión por la mención de un grupo criminal solicitando una colaboración de forma aparentemente cortés."
                )
            # Verificar otras combinaciones comunes
            elif "banda" in text_lower and ("colaboración" in text_lower or "colaborar" in text_lower):
                return ThreatAnalysis(
                    keyword="colaboración con banda",
                    threat_type=ThreatType.EXTORSION,
                    is_threat="SI",
                    justification="Se detectó una posible extorsión por mencionar una banda criminal solicitando una colaboración."
                )
            # Verificar ofertas de "seguridad" o "protección" no solicitadas
            elif ("ofrecemos" in text_lower or "ofrecer" in text_lower) and ("seguridad" in text_lower or "protección" in text_lower):
                return ThreatAnalysis(
                    keyword="ofrecimiento de seguridad",
                    threat_type=ThreatType.EXTORSION,
                    is_threat="SI",
                    justification="Se detectó una posible extorsión por el ofrecimiento no solicitado de servicios de 'seguridad' o 'protección'."
                )
            elif any(keyword in text_lower for keyword in extorsion_keywords):
                keyword = next((kw for kw in extorsion_keywords if kw in text_lower), "vacuna")
                return ThreatAnalysis(
                    keyword=keyword,
                    threat_type=ThreatType.EXTORSION,
                    is_threat="SI",
                    justification=f"Se detectó una posible extorsión por el uso de la palabra '{keyword}'."
                )
            elif any(keyword in text_lower for keyword in robo_keywords):
                keyword = next((kw for kw in robo_keywords if kw in text_lower), "susto")
                return ThreatAnalysis(
                    keyword=keyword,
                    threat_type=ThreatType.ROBO,
                    is_threat="SI",
                    justification=f"Se detectó una posible amenaza de robo por el uso de la palabra '{keyword}'."
                )
            elif any(keyword in text_lower for keyword in secuestro_keywords):
                keyword = next((kw for kw in secuestro_keywords if kw in text_lower), "vuelta")
                return ThreatAnalysis(
                    keyword=keyword,
                    threat_type=ThreatType.SECUESTRO,
                    is_threat="SI",
                    justification=f"Se detectó una posible amenaza de secuestro por el uso de la palabra '{keyword}'."
                )
            else:
                return ThreatAnalysis(
                    keyword="ninguna",
                    threat_type=ThreatType.NINGUNA,
                    is_threat="NO",
                    justification="No se detectaron palabras o frases relacionadas con amenazas."
                )
        except Exception as e:
            print(f"Error en el simulador: {str(e)}")
            return ThreatAnalysis(
                keyword="error_simulador",
                threat_type=ThreatType.NINGUNA,
                is_threat="NO",
                justification=f"Ocurrió un error al analizar el texto: {str(e)}"
            )
