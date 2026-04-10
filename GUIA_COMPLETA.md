# 📖 Guía Completa de Instalación y Configuración

Esta guía detalla los pasos necesarios para desplegar el **Sistema Multiagente de Análisis Documental** desde cero.

---

## 🛠️ Requisitos Previos

1.  **Suscripción de Azure**: Necesitarás acceso a:
    -   Azure Blob Storage.
    -   Azure AI Search.
    -   Azure AI Document Intelligence (v4.0).
2.  **Cuenta de OpenAI**: API Key para GPT-4o y Embeddings.
3.  **Python 3.10+** instalado localmente.

---

## 🔧 Configuración Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/rg-multiagente.git
cd rg-multiagente
```

### 2. Entorno Virtual y Dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto con los siguientes campos:

```env
# Azure Storage
AZURE_STORAGE_CONNECTION="tu_cadena_de_conexion"
AZURE_STORAGE_CONTAINER="documentos"

# Azure AI Search
AZURE_SEARCH_ENDPOINT="https://tu-servicio.search.windows.net"
AZURE_SEARCH_KEY="tu_llave_admin"
AZURE_SEARCH_INDEX="idx-documentos"

# Azure Document Intelligence
DOCUMENTINTELLIGENCE_ENDPOINT="https://tu-servicio.cognitiveservices.azure.com/"
DOCUMENTINTELLIGENCE_API_KEY="tu_llave"

# OpenAI
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-4o"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
```

### 4. Inicializar Infraestructura de Búsqueda
Ejecuta el script de configuración para crear el índice vectorial en Azure:
```bash
python setup_azure.py
```

---

## 🚀 Ejecución del Sistema

### Iniciar la API (Flask)
```bash
python app.py
```
La API estará disponible en `http://localhost:5000`.

### Probar el Sistema
Puedes usar **Postman** o `curl` para subir un documento:

```bash
curl -X POST -F "archivo=@contrato_1.pdf" http://localhost:5000/procesar
```

---

## 🧪 Pruebas Locales
Para verificar que todos los agentes están funcionando correctamente sin usar la API:
```bash
python test_local.py
```

---

## 📂 Estructura del Proyecto
- `agents/`: Lógica de los agentes (Extractor, Analyzer, Validator, Reporter).
- `tools/`: Utilidades para Azure Storage y Search.
- `app.py`: Punto de entrada de la API Flask.
- `frontend/`: Interfaz básica de usuario.
