# 📚 Documentación Técnica Completa

Esta sección detalla cada módulo, clase y función del **Sistema Multiagente de Análisis Documental**.

---

## 🏛️ Agentes del Sistema

### 1. [Orchestrator](agents/orchestrator.py)
El cerebro del sistema. Coordina el flujo de datos entre todos los agentes y herramientas.
- **`__init__()`**: Inicializa todos los agentes y herramientas.
- **`procesar_documento(ruta_archivo)`**: 
  - **Entrada**: Ruta local del archivo.
  - **Salida**: Diccionario con el análisis completo, URLs de almacenamiento y reporte.
  - **Lógica**: Ejecuta un pipeline de 6 pasos (Storage -> Extracción -> Análisis -> Validación -> Indexación -> Reporte). Incluye logging estructurado y métricas de tiempo.
- **`responder_pregunta(pregunta)`**: 
  - **Entrada**: String con la consulta del usuario.
  - **Salida**: Respuesta generada basada en el contexto de los documentos cargados (RAG).

### 2. [ExtractorAgent](agents/extractor_agent.py)
Responsable del OCR y la digitalización.
- **`extraer(ruta_archivo)`**: Usa Azure Document Intelligence (modelo `prebuilt-layout`) para extraer texto, tablas y párrafos. Devuelve un diccionario con el contenido estructurado.

### 3. [AnalyzerAgent](agents/analyzer_agent.py)
Encargado de la interpretación semántica.
- **`analizar(texto)`**: Utiliza OpenAI GPT-4o para resumir, clasificar y extraer entidades. Implementa RAG consultando documentos previos similares para mayor precisión.
- **`responder_pregunta(pregunta)`**: Genera respuestas concisas basadas únicamente en los fragmentos de documentos recuperados de Azure AI Search.

### 4. [ValidatorAgent](agents/validator_agent.py)
Aplica reglas de negocio sobre el análisis generado.
- **`validar(analisis)`**: Compara las entidades extraídas contra reglas configurables (montos máximos, fechas críticas, palabras clave).
- **`recargar_reglas()`**: Recarga el archivo `data/reglas.json` en tiempo real sin reiniciar el sistema.

### 5. [ReporterAgent](agents/reporter_agent.py)
Generador de documentos finales.
- **`generar_reporte(resultado, doc_id)`**: Crea un PDF profesional utilizando la librería `fpdf2` que resume todo el proceso de análisis y validación.

---

## 🛠️ Herramientas de Infraestructura

### 1. [SearchTool](tools/search_tool.py)
Interfaz con Azure AI Search.
- **`_obtener_embedding(texto)`**: Convierte texto en vectores de 1536 dimensiones usando el modelo `text-embedding-3-small`.
- **`indexar_documento(...)`**: Sube el contenido y su vector correspondiente al índice de búsqueda.
- **`buscar_similares(consulta, top)`**: Realiza búsquedas vectoriales (HNSW) para encontrar los fragmentos más relevantes para el RAG.

### 2. [StorageTool](tools/storage_tool.py)
Interfaz con Azure Blob Storage.
- **`subir_archivo(ruta_local, nombre_blob)`**: Sube archivos originales y reportes generados a la nube, retornando la URL pública/privada de acceso.

---

## 🔌 API Flask (app.py)

Endpoints protegidos por el header `X-API-Key`.

### `GET /health`
- **Público**. Verifica el estado del sistema.

### `POST /procesar`
- **Protegido**. Recibe un archivo (form-data: `archivo`). Inicia el pipeline multiagente.

### `POST /preguntar`
- **Protegido**. Recibe un JSON `{"pregunta": "..."}`. Devuelve una respuesta basada en los documentos indexados.

---

## 📝 Registro y Monitoreo
El sistema utiliza un **Logging Estructurado** en `logs/pipeline.log`:
- **Nivel INFO**: Seguimiento de pasos y tiempos de ejecución.
- **Nivel WARNING**: Problemas no críticos (ej: Blob Storage no disponible).
- **Nivel ERROR**: Excepciones críticas con Traceback completo para debugging.
- **Rotación**: Archivos de máximo 10MB con 5 respaldos históricos.
