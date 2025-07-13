"""API REST para el servicio de detección de amenazas."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.application.use_cases import AnalyzeTextUseCase
from src.infrastructure.config import Config
from src.infrastructure.threat_detector import DeepSeekThreatDetector
from src.infrastructure.mock_threat_detector import MockDeepSeekThreatDetector
from src.infrastructure.static_files import setup_static_files


class TextAnalysisRequest(BaseModel):
    """Modelo para la solicitud de análisis de texto."""
    
    text: str = Field(..., description="Texto a analizar para detectar amenazas")


class ThreatDetectionAPI:
    """API REST para el servicio de detección de amenazas."""
    
    def __init__(self):
        """Inicializa la API."""
        self._app = FastAPI(
            title="Kuntur Detector API",
            description="API para la detección de amenazas en negocios ecuatorianos",
            version="0.1.0"
        )
        
        # Configurar CORS
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # En producción, especificar orígenes concretos
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Inicializar dependencias
        if Config.USE_MOCK:
            self._threat_detector = MockDeepSeekThreatDetector()
        else:
            self._threat_detector = DeepSeekThreatDetector()
        self._analyze_use_case = AnalyzeTextUseCase(self._threat_detector)
        
        # Configurar archivos estáticos
        setup_static_files(self._app)
        
        # Configurar rutas
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura las rutas de la API."""
        
        @self._app.post("/analysis", tags=["Amenazas"])
        async def analyze_text(request: TextAnalysisRequest):
            """Analiza un texto para detectar amenazas.
            
            Args:
                request: Solicitud con el texto a analizar
                
            Returns:
                Resultado del análisis de amenazas
            """
            try:
                result = await self._analyze_use_case.execute(request.text)
                return result.model_dump()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al analizar el texto: {str(e)}")
        
        @self._app.get("/health", tags=["Sistema"])
        async def health_check():
            """Verifica el estado del sistema."""
            return {"status": "ok"}
    
    @property
    def app(self):
        """Obtiene la instancia de FastAPI.
        
        Returns:
            La instancia de FastAPI
        """
        return self._app
