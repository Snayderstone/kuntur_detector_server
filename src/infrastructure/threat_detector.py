"""Adaptador para la API de DeepSeek."""

import os
import json
import logging
from typing import Dict, List, Any

import httpx
from dotenv import load_dotenv

from src.domain.models import ThreatAnalysis, ThreatType
from src.domain.ports import ThreatDetectorPort
from src.infrastructure.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("deepseek_detector")

# Prompt para la detección de amenazas adaptado al contexto ecuatoriano
THREAT_DETECTION_PROMPT = """
Eres un sistema experto en seguridad especializado en analizar el CONTEXTO e INTENCIÓN de mensajes para detectar amenazas en Ecuador.

TAREA: Analiza el siguiente texto y determina si contiene una amenaza implícita o explícita de extorsión, robo o secuestro.

CONTEXTO ECUATORIANO:
Es fundamental que evalúes tanto el lenguaje explícito como la intención oculta. Muchas amenazas utilizan un lenguaje cortés, formal y ambiguo pero con claras intenciones amenazantes. Debes detectar estas amenazas SUTILES.

Ejemplos de amenazas disfrazadas con lenguaje cortés:
1. "Buenos días vecina, le saluda la banda de los lobos para pedirle una pequeña colaboración" → EXTORSIÓN (solicitud de dinero por una banda criminal bajo apariencia cortés)
2. "Le vamos a visitar para conversar sobre la seguridad de su negocio" → EXTORSIÓN (implica consecuencias si no se paga)
3. "Necesitamos que coopere con la causa para evitar problemas" → EXTORSIÓN (implica consecuencias negativas)
4. "Queremos ofrecerle un servicio de protección para su local" → EXTORSIÓN (cuando viene de grupos criminales)
5. "Pasaremos a conocer su casa y a su familia" → AMENAZA/INTIMIDACIÓN (implica vigilancia)
6. "Si no llega a un acuerdo, no podemos garantizar que esté seguro" → EXTORSIÓN
7. "Solo queremos presentarnos con usted para que nos conozca, somos la gente que trabaja en este sector" → EXTORSIÓN (presentación intimidante)
8. "Por su seguridad, es mejor que hablemos personalmente sobre un tema de interés mutuo" → AMENAZA VELADA

JERGA ECUATORIANA COMÚN EN AMENAZAS:
- "vacunas/vacunita" = pagos de extorsión/protección
- "colaboración/colaborar/aporte/apoyar" = pago forzado
- "dar el susto" = robo o ataque
- "llevar pa' la vuelta" = secuestro
- "tocar la puerta" = amenaza de visita
- "visitar el local/negocio" = amenaza de daños
- "hacer limpieza" = amenaza de daño físico
- "servicio de seguridad" = extorsión
- "estar pendiente" = vigilancia amenazante
- "conocer a la familia" = amenaza velada
- "prevenir problemas/accidentes" = amenaza velada
- "la gente/los muchachos del sector" = grupo criminal local

ANALIZAR CON ESPECIAL ATENCIÓN:
- Referencias a grupos/bandas/organizaciones (incluso con nombres que parecen inofensivos)
- Solicitudes de dinero/pagos/colaboraciones con tono cordial pero intimidante
- Lenguaje aparentemente amable o formal pero con intenciones amenazantes subyacentes
- Ofrecimientos de "protección", "seguridad" o "prevención" no solicitados
- Menciones a conocer detalles personales (familia, dirección, rutinas)
- Consecuencias implícitas de no cooperar o no aceptar una propuesta
- Presentaciones de grupos o personas que "controlan" o "trabajan" en la zona

Texto a analizar: "{text}"

FORMATO DE RESPUESTA:
Tipo: <extorsión/robo/secuestro/ninguna>
Palabra clave: <palabra o frase clave que indica la amenaza>
Justificación: <Explicación detallada de por qué es una amenaza, basada tanto en palabras específicas como en el contexto y la intención percibida. Si es una amenaza disfrazada con lenguaje cortés, explica cómo se identifica la intención real detrás de las palabras utilizadas>
"""

class DeepSeekThreatDetector(ThreatDetectorPort):
    """Adaptador para la API de DeepSeek que implementa la detección de amenazas."""
    
    def __init__(self, api_key: str = ""):
        """Inicializa el adaptador.
        
        Args:
            api_key: Clave de API para DeepSeek (opcional, por defecto se toma de variables de entorno)
        """
        self._api_key = api_key or Config.DEEPSEEK_API_KEY or "sk-bbf05858555647b28e9f0b65d6e19896"
        self._api_url = Config.DEEPSEEK_API_URL
        
    async def analyze_text(self, text: str) -> ThreatAnalysis:
        """Analiza un texto y determina si contiene amenazas utilizando DeepSeek.
        
        Args:
            text: El texto a analizar
            
        Returns:
            El análisis de la amenaza
        """
        logger.info(f"Analizando texto: {text[:50]}...")
        prompt = THREAT_DETECTION_PROMPT.format(text=text)
        logger.debug(f"Prompt generado: {prompt[:100]}...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    # Preparar la solicitud
                    # Configurar la solicitud según documentación de la API de DeepSeek
                    headers = {
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    request_data = {
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,  # Baja temperatura para respuestas más deterministas
                        "max_tokens": 150,
                        "stream": False
                    }
                    
                    logger.info(f"Conectando a DeepSeek API URL: {self._api_url}")
                    logger.debug(f"Headers de autorización configurados")
                    logger.debug(f"Request data: {json.dumps(request_data)}")
                    
                    response = await client.post(
                        self._api_url,
                        headers=headers,
                        json=request_data,
                        timeout=30.0
                    )
                    
                    logger.info(f"Respuesta recibida con código: {response.status_code}")
                    
                    if response.status_code != 200:
                        logger.error(f"Error en la API de DeepSeek: {response.status_code} - {response.text}")
                        # Fallback a una respuesta predeterminada en caso de error
                        return ThreatAnalysis(
                            keyword="error_api",
                            threat_type=ThreatType.NINGUNA,
                            is_threat="NO",
                            justification="No se pudo analizar el texto debido a un error en la API externa."
                        )
                    
                    response_data = response.json()
                    logger.info("Respuesta JSON recibida correctamente")
                    logger.debug(f"Respuesta completa: {json.dumps(response_data)}")
                    
                    # Procesar la respuesta
                    raw_result = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    logger.info(f"Respuesta raw del modelo: {raw_result}")
                    
                    # Extraer tipo, palabra clave y justificación de la respuesta
                    threat_type_line = next((line for line in raw_result.split("\n") 
                                    if line.startswith("Tipo:") or line.lower().startswith("tipo:")), "Tipo: ninguna")
                    keyword_line = next((line for line in raw_result.split("\n") 
                                    if line.startswith("Palabra clave:") or line.lower().startswith("palabra clave:")), 
                                    "Palabra clave: ninguna")
                    justification_line = next((line for line in raw_result.split("\n") 
                                    if line.startswith("Justificación:") or line.lower().startswith("justificacion:") 
                                    or line.lower().startswith("justificación:")), 
                                    "Justificación: No se proporcionó justificación.")
                    
                    # Extraer valores
                    threat_type_str = threat_type_line.split(":", 1)[1].strip().lower()
                    keyword = keyword_line.split(":", 1)[1].strip()
                    justification = justification_line.split(":", 1)[1].strip()
                    
                    logger.info(f"Tipo de amenaza extraído: {threat_type_str}")
                    logger.info(f"Palabra clave extraída: {keyword}")
                    logger.info(f"Justificación extraída: {justification}")
                    
                    # Mapear a ThreatType
                    if "extorsión" in threat_type_str or "extorsion" in threat_type_str:
                        threat_type = ThreatType.EXTORSION
                    elif "robo" in threat_type_str:
                        threat_type = ThreatType.ROBO
                    elif "secuestro" in threat_type_str:
                        threat_type = ThreatType.SECUESTRO
                    else:
                        threat_type = ThreatType.NINGUNA
                    
                    # Determinar si es una amenaza
                    is_threat = "SI" if threat_type != ThreatType.NINGUNA else "NO"
                    logger.info(f"Decisión final: {is_threat}, tipo: {threat_type}")
                    
                    return ThreatAnalysis(
                        keyword=keyword,
                        threat_type=threat_type,
                        is_threat=is_threat,
                        justification=justification
                    )
                    
                except Exception as e:
                    logger.exception(f"Error al comunicarse con la API de DeepSeek: {str(e)}")
                    # Fallback a una respuesta predeterminada en caso de error
                    return ThreatAnalysis(
                        keyword="error_comunicacion",
                        threat_type=ThreatType.NINGUNA,
                        is_threat="NO",
                        justification="No se pudo establecer comunicación con la API de análisis."
                    )
        except Exception as e:
            logger.exception(f"Error general al procesar la petición: {str(e)}")
            # Fallback a una respuesta predeterminada en caso de error
            return ThreatAnalysis(
                keyword="error_general",
                threat_type=ThreatType.NINGUNA,
                is_threat="NO",
                justification="Ocurrió un error general al procesar la solicitud."
            )
            raw_result = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Extraer tipo y palabra clave de la respuesta
            threat_type_line = next((line for line in raw_result.split("\n") 
                              if line.startswith("Tipo:") or line.lower().startswith("tipo:")), "Tipo: ninguna")
            keyword_line = next((line for line in raw_result.split("\n") 
                              if line.startswith("Palabra clave:") or line.lower().startswith("palabra clave:")), 
                              "Palabra clave: ninguna")
            
            # Extraer valores
            threat_type_str = threat_type_line.split(":", 1)[1].strip().lower()
            keyword = keyword_line.split(":", 1)[1].strip()
            
            # Mapear a ThreatType
            if "extorsión" in threat_type_str or "extorsion" in threat_type_str:
                threat_type = ThreatType.EXTORSION
            elif "robo" in threat_type_str:
                threat_type = ThreatType.ROBO
            elif "secuestro" in threat_type_str:
                threat_type = ThreatType.SECUESTRO
            else:
                threat_type = ThreatType.NINGUNA
            
            # Determinar si es una amenaza
            is_threat = "SI" if threat_type != ThreatType.NINGUNA else "NO"
            
            return ThreatAnalysis(
                keyword=keyword,
                threat_type=threat_type,
                is_threat=is_threat
            )
