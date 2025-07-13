"""Adaptador para la API de DeepSeek."""

import os
import json
import time
import logging
import hashlib
import asyncio
import functools
from typing import Dict, List, Any, Optional, Tuple

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

# Prompt ultra-eficiente para detección de amenazas
ULTRA_EFFICIENT_PROMPT = """
Analiza: "{text}"

Identifica: amenazas explícitas/implícitas (extorsión/robo/secuestro) en contexto ecuatoriano.
Alerta: lenguaje cordial con intención amenazante ("colaboración", "protección", "visita").

Formato exacto:
Tipo: <extorsión/robo/secuestro/ninguna>
Palabra: <término clave>
Por qué: <explicación concisa>
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
        self._cache = {}
        self._cache_ttl = Config.CACHE_TTL_HOURS * 60 * 60  # Convertir horas a segundos
        self._use_cache = Config.USE_CACHE
        
    def _generate_cache_key(self, text: str) -> str:
        """Genera una clave de caché para el texto usando un hash MD5."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"threat_detector:{text_hash}"
        
    async def analyze_text(self, text: str) -> ThreatAnalysis:
        """Analiza un texto y determina si contiene amenazas utilizando DeepSeek.
        
        Args:
            text: El texto a analizar
            
        Returns:
            El análisis de la amenaza
        """
        logger.info(f"Analizando texto: {text[:50]}...")
        
        # Verificar caché si está habilitada
        if self._use_cache:
            text_hash = hashlib.md5(text.encode()).hexdigest()
            logger.debug(f"Verificando caché para texto (hash: {text_hash})")
            cache_key = self._generate_cache_key(text)
            logger.debug(f"Generando clave de caché: {cache_key}")
            
            # Verificar si hay resultado en caché y no ha expirado
            if cache_key in self._cache:
                cached_result, timestamp = self._cache[cache_key]
                current_time = time.time()
                
                if current_time - timestamp < self._cache_ttl:
                    logger.info("Resultado encontrado en caché!")
                    return cached_result
                else:
                    # Eliminar entrada expirada
                    del self._cache[cache_key]
                    logger.debug("Caché expirada, consultando API")
            else:
                logger.info("Caché no encontrada, consultando API")
        else:
            logger.debug("Verificando caché para texto (caché desactivada)")
        
        # Si no hay caché o está desactivada, hacer llamada a la API
        prompt = ULTRA_EFFICIENT_PROMPT.format(text=text)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    # Preparar la solicitud
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
                    logger.debug(f"Procesando respuesta: {json.dumps(response_data)}")
                    
                    # Procesar la respuesta
                    raw_result = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # Extraer tipo, palabra clave y justificación de la respuesta
                    threat_type_line = next((line for line in raw_result.split("\n") 
                                    if line.startswith("Tipo:") or line.lower().startswith("tipo:")), "Tipo: ninguna")
                    keyword_line = next((line for line in raw_result.split("\n") 
                                    if line.startswith("Palabra:") or line.lower().startswith("palabra:")), 
                                    "Palabra: ninguna")
                    justification_line = next((line for line in raw_result.split("\n") 
                                    if line.startswith("Por qué:") or line.lower().startswith("por que:") 
                                    or line.lower().startswith("por qué:")), 
                                    "Por qué: No se proporcionó justificación.")
                    
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
                    
                    # Crear objeto de análisis de amenaza
                    threat_analysis = ThreatAnalysis(
                        keyword=keyword,
                        threat_type=threat_type,
                        is_threat=is_threat,
                        justification=justification
                    )
                    
                    # Guardar en caché si está habilitada
                    if self._use_cache:
                        cache_key = self._generate_cache_key(text)
                        self._cache[cache_key] = (threat_analysis, time.time())
                        logger.debug(f"Guardando resultado en caché con clave: {cache_key}")
                    
                    return threat_analysis
                
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
