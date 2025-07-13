# Kuntur Detector Server

Sistema de detección de amenazas en tiempo real para negocios ecuatorianos.

## Descripción

Kuntur Detector es un servicio que analiza textos recibidos (como mensajes, correos, etc.) para identificar posibles amenazas de extorsión, robo o secuestro, utilizando lenguaje natural procesado por un modelo de IA especializado en reconocer jerga ecuatoriana utilizada en contextos de amenazas.

## Características

- API REST con endpoint `/analysis` para análisis de textos
- Detección de tres tipos de amenazas: extorsión, robo y secuestro
- Procesamiento mediante API de DeepSeek con prompt especializado
- Frontend ultraligero para pruebas
- Arquitectura hexagonal (puertos y adaptadores) para mantener el código limpio y flexible

## Estructura del Proyecto

```
kuntur_detector_server/
├── src/                      # Código fuente
│   ├── domain/               # Capa de dominio: entidades y reglas de negocio
│   ├── application/          # Capa de aplicación: casos de uso
│   └── infrastructure/       # Capa de infraestructura: adaptadores externos
├── tests/                    # Pruebas unitarias
├── ui/                       # Frontend básico
├── main.py                   # Punto de entrada del servidor
├── pyproject.toml            # Dependencias del proyecto
└── README.md                 # Documentación
```

## Instalación

1. Clona este repositorio:

```bash
git clone https://github.com/tu-usuario/kuntur-detector-server.git
cd kuntur-detector-server
```

2. Instala las dependencias:

```bash
uv add fastapi uvicorn httpx pydantic pytest python-dotenv
```

3. Configura las variables de entorno:

Crea un archivo `.env` en la raíz del proyecto con:

```
HOST=0.0.0.0
PORT=8000
DEEPSEEK_API_KEY=tu_api_key_de_deepseek
```

## Ejecución

Para iniciar el servidor:

```bash
python main.py
```

El servidor estará disponible en `http://localhost:8000`.

## Uso de la API

### Analizar un texto

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text": "El texto a analizar"}' http://localhost:8000/analysis
```

Respuesta:

```json
{
  "keyword": "palabra_clave_detectada",
  "threat_type": "extorsión|robo|secuestro|ninguna",
  "is_threat": "SI|NO"
}
```

## Frontend

Un frontend simple está disponible en `http://localhost:8000/ui/index.html` para pruebas.

## Ejecutar Tests

Para ejecutar las pruebas unitarias:

```bash
pytest
```

## Licencia

MIT