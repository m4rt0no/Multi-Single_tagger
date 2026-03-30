# Multitag API

> **Repositorio prototipo** — Base experimental lista para usar como punto de partida en proyectos de clasificación automática de mensajes con IA. Clona, configura tu cliente y empieza a clasificar en minutos.

API de clasificación automática de mensajes utilizando inteligencia artificial. Permite clasificar correos electrónicos, tweets o tickets de soporte en múltiples categorías configurables y generar respuestas automáticas.

## Características

- **Clasificación inteligente**: Utiliza OpenAI GPT-4.1 para clasificar mensajes
- **Múltiples categorías**: Soporte para clasificación en una o múltiples categorías simultáneas
- **Configuración por cliente**: Cada cliente define sus propias categorías y plantillas de respuesta en archivos JSON
- **Respuestas automáticas**: Generación de respuestas basadas en plantillas personalizadas
- **API REST**: Interfaz simple y rápida construida con FastAPI

## Estructura del Proyecto

```
multitag-api/
├── main.py                  # Definición de endpoints FastAPI
├── func.py                  # Lógica de clasificación y generación de respuestas
├── prompts.py               # Prompts del sistema para el modelo de IA
├── config.py                # Configuración y variables de entorno
├── requirements.txt
├── Dockerfile
├── clients/
│   └── test-client/         # Cliente de ejemplo incluido
│       ├── lista_test-client.json       # Categorías del cliente
│       └── templates_test-client.json  # Plantillas de respuesta
├── charts/multitag-api/     # Helm chart para despliegue en Kubernetes
└── tests/
    ├── conftest.py
    └── test_generic_endpoints.py
```

## Inicio Rápido

### Prerequisitos

- Python 3.8+
- Clave API de OpenAI

### Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd multitag-api
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
# Crear archivo .env en la raíz del proyecto
echo "OPENAI_API_KEY=tu_clave_api_de_openai" > .env
```

4. **Ejecutar la aplicación**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`.

## Endpoints

### 1. Health Check
```
GET /healthz
```
Verifica el estado de la API.

**Respuesta:**
```json
{
  "status": "ok"
}
```

### 2. Clasificación con Respuesta (Múltiples Categorías)
```
POST /tag
```
Clasifica el mensaje en múltiples categorías y genera una respuesta automática.

**Solicitud:**
```json
{
  "text": "El mensaje a clasificar",
  "client": "nombre-del-cliente"
}
```

**Respuesta:**
```json
{
  "categorias": [
    "TST001 - Consulta simple",
    "TST002 - Reclamo postventa"
  ],
  "response": "Respuesta generada automáticamente"
}
```

### 3. Solo Clasificación (Múltiples Categorías)
```
POST /tag_only
```
Clasifica el mensaje sin generar respuesta.

**Solicitud:**
```json
{
  "text": "El mensaje a clasificar",
  "client": "nombre-del-cliente"
}
```

**Respuesta:**
```json
{
  "TST001": 1,
  "TST002": 0,
  "TST999": 0
}
```

### 4. Clasificación con Respuesta (Categoría Única)
```
POST /tag_single
```
Clasifica el mensaje en la categoría más relevante y genera respuesta.

**Solicitud:**
```json
{
  "text": "El mensaje a clasificar",
  "client": "nombre-del-cliente"
}
```

**Respuesta:**
```json
{
  "categorias": [
    "TST001 - Consulta simple"
  ],
  "response": "Respuesta específica para esta categoría"
}
```

## Ejemplos de Uso

Los ejemplos usan el cliente `test-client` incluido en el repositorio.

### Ejemplo 1: Clasificación completa
```bash
curl -X POST "http://localhost:8000/tag" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hola, quisiera saber el horario de atención",
    "client": "test-client"
  }'
```

**Respuesta:**
```json
{
  "categorias": [
    "TST001 - Consulta simple"
  ],
  "response": "Gracias por tu consulta. Para más información, contáctanos por interno."
}
```

### Ejemplo 2: Solo clasificación
```bash
curl -X POST "http://localhost:8000/tag_only" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mi pedido no ha llegado y ya pasó una semana",
    "client": "test-client"
  }'
```

**Respuesta:**
```json
{
  "TST001": 0,
  "TST002": 1,
  "TST999": 0
}
```

### Ejemplo 3: Clasificación única
```bash
curl -X POST "http://localhost:8000/tag_single" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Necesito hablar con alguien urgente",
    "client": "test-client"
  }'
```

**Respuesta:**
```json
{
  "categorias": [
    "TST999 - Derivar a DM"
  ],
  "response": "Por favor envíanos un mensaje directo para derivarte con un ejecutivo."
}
```

## Configuración de Clientes

Cada cliente se define mediante dos archivos JSON dentro de su propia carpeta en `clients/`.

### Estructura de Carpetas
```
clients/
└── nombre-cliente/
    ├── lista_nombre-cliente.json       # Categorías disponibles
    └── templates_nombre-cliente.json  # Plantillas de respuesta por categoría
```

### Archivo de Categorías (`lista_nombre-cliente.json`)

Define las categorías en las que se clasificarán los mensajes. El formato es un objeto JSON con claves únicas por categoría y una descripción detallada como valor. La descripción se incluye en el prompt del modelo para guiar la clasificación.

```json
{
  "CAT001": "Nombre de categoría [Descripción detallada para el modelo]",
  "CAT002": "Otra categoría [Descripción detallada para el modelo]",
  "CAT000": "Otro tipo de mensaje [Categoría de fallback para mensajes sin clasificación clara]"
}
```

### Archivo de Plantillas (`templates_nombre-cliente.json`)

Define la respuesta automática asociada a cada categoría. Si una categoría no tiene plantilla, la respuesta será `"Sin respuesta"`.

```json
{
  "CAT001": "Texto de respuesta automática para CAT001",
  "CAT002": "Texto de respuesta automática para CAT002"
}
```

### Cliente de Ejemplo Incluido

El repositorio incluye `clients/test-client/` como referencia funcional:

```json
// lista_test-client.json
{
  "TST001": "Consulta simple [Pregunta general sin impacto operacional]",
  "TST002": "Reclamo postventa [Problemas luego de la compra]",
  "TST999": "Derivar a DM [Casos que requieren atención manual]"
}
```

```json
// templates_test-client.json
{
  "TST001": "Gracias por tu consulta. Para más información, contáctanos por interno.",
  "TST002": "Lamentamos lo ocurrido. Escríbenos por mensaje privado para ayudarte.",
  "TST999": "Por favor envíanos un mensaje directo para derivarte con un ejecutivo."
}
```

## Manejo de Errores

### Error 400 - Solicitud Incorrecta
```json
{
  "error": "Falta la clave 'text' en el cuerpo de la solicitud"
}
```

### Error 500 - Error Interno
```json
{
  "error": "Error interno: Descripción del error"
}
```

## Respuestas Especiales

- **Sin respuesta**: Cuando no existe plantilla para la categoría seleccionada, se devuelve `"Sin respuesta"`
- **Categoría por defecto**: Si el modelo no puede clasificar el mensaje, se asigna la categoría `"CAT000 - Otro tipo de Mensaje"`

## Consideraciones Técnicas

- **Modelo**: OpenAI GPT-4.1
- **Temperatura**: 0 para clasificación, 0.4 para generación de respuestas
- **Formato de salida**: JSON estricto para clasificación
- **Encoding**: UTF-8 para soporte completo de caracteres especiales

## Tests

```bash
pytest -q
```

Los tests se ejecutan con un mock del cliente OpenAI; no requieren clave API real.

## Despliegue

### Docker

```bash
docker build -t multitag-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=tu_clave multitag-api
```

Las variables de runtime están definidas en el `Dockerfile` y se pueden sobreescribir al lanzar el contenedor:

| Variable | Por defecto | Descripción |
|---|---|---|
| `OPENAI_API_KEY` | — | Clave de API de OpenAI (obligatoria) |
| `WORKERS` | `4` | Número de workers de uvicorn |
| `SEMAPHORE` | `20` | Concurrencia máxima de peticiones simultáneas |

### Kubernetes

Helm chart disponible en `charts/multitag-api/` con soporte para entornos de staging y producción.

```bash
helm upgrade --install multitag-api ./charts/multitag-api \
  --namespace production \
  --set image.repository=tu-registry/multitag-api \
  --set image.tag=latest
```

### CI/CD (GitHub Actions)

El repositorio incluye `.github/workflows/ci.yml` con dos jobs:

- **test**: instala dependencias y ejecuta `pytest` en cada push/PR a `main`
- **build**: construye la imagen Docker tras pasar los tests

Para habilitar el push automático al registry, descomenta los pasos de `login` y `push` en el workflow y configura estos secrets en GitHub:

| Secret | Descripción |
|---|---|
| `REGISTRY` | URL del registry (ej. `ghcr.io` o `docker.io`) |
| `REGISTRY_USER` | Usuario o service account |
| `REGISTRY_TOKEN` | Password o Personal Access Token |

## Contribuir

1. Crea una rama desde `main`
2. Agrega tu cliente en `clients/nombre-cliente/`
3. Verifica que los tests pasen con `pytest -q`
4. Abre un Pull Request
