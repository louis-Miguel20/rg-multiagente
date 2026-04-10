import os
import uuid
import time
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agents.extractor_agent import ExtractorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.validator_agent import ValidatorAgent
from agents.reporter_agent import ReporterAgent
from tools.search_tool import SearchTool
from tools.storage_tool import StorageTool

# Configuración de logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger("pipeline")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Handler para archivo con rotación (máximo 10MB, 5 archivos de respaldo)
# Aunque se pidió rotación diaria, RotatingFileHandler suele usarse con tamaño. 
# Para rotación diaria estricta se usaría TimedRotatingFileHandler. 
# Usaré RotatingFileHandler como se solicitó explícitamente.
file_handler = RotatingFileHandler(
    os.path.join(log_dir, "pipeline.log"), 
    maxBytes=10*1024*1024, 
    backupCount=5
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class Orchestrator:
    """
    Orquestador central: coordina el flujo completo de 5 agentes.
    Cada agente es independiente y reemplazable.
    """

    def __init__(self):
        self.extractor = ExtractorAgent()
        self.analyzer = AnalyzerAgent()
        self.validator = ValidatorAgent()
        self.reporter = ReporterAgent()
        self.search = SearchTool()
        self.storage = StorageTool()

    def procesar_documento(self, ruta_archivo: str) -> dict:
        nombre = Path(ruta_archivo).name
        doc_id = str(uuid.uuid4())
        inicio_total = time.time()

        logger.info(f"Iniciando pipeline: {nombre} | ID: {doc_id}")

        try:
            # PASO 1: Subir a Blob Storage
            inicio_paso = time.time()
            try:
                url_blob = self.storage.subir_archivo(ruta_archivo, f"{doc_id}_{nombre}")
                logger.info(f"PASO 1 (Storage) finalizado en {time.time() - inicio_paso:.2f}s | URL: {url_blob}")
            except Exception as e:
                logger.warning(f"PASO 1 (Storage) falló: {e}")
                url_blob = None

            # PASO 2: Extraer contenido con Document Intelligence
            inicio_paso = time.time()
            extraccion = self.extractor.extraer(ruta_archivo)
            logger.info(f"PASO 2 (Extraction) finalizado en {time.time() - inicio_paso:.2f}s | Páginas: {extraccion['num_paginas']}")

            if not extraccion["tiene_texto"]:
                logger.warning(f"Documento sin texto legible: {doc_id}")
                return {
                    "error": "El documento no contiene texto legible.",
                    "doc_id": doc_id,
                }

            # PASO 3: Analizar con GPT-4o + RAG
            inicio_paso = time.time()
            analisis = self.analyzer.analizar(extraccion["texto"])
            logger.info(f"PASO 3 (Analysis) finalizado en {time.time() - inicio_paso:.2f}s | Tipo: {analisis.get('tipo_documento')}")

            # PASO 4: Validar contra reglas de negocio
            inicio_paso = time.time()
            validacion = self.validator.validar(analisis)
            logger.info(f"PASO 4 (Validation) finalizado en {time.time() - inicio_paso:.2f}s | Válido: {validacion['valido']}")

            # PASO 5: Indexar en Azure AI Search
            inicio_paso = time.time()
            self.search.indexar_documento(
                doc_id=doc_id,
                contenido=extraccion["texto"],
                tipo_doc=analisis.get("tipo_documento", "otro"),
                nombre_archivo=nombre,
            )
            logger.info(f"PASO 5 (Search Indexing) finalizado en {time.time() - inicio_paso:.2f}s")

            # PASO 6: Generar reporte ejecutivo
            inicio_paso = time.time()
            res_completo = {
                "doc_id": doc_id,
                "nombre_archivo": nombre,
                "num_paginas": extraccion["num_paginas"],
                "tipo_documento": analisis.get("tipo_documento"),
                "resumen": analisis.get("resumen"),
                "entidades": analisis.get("entidades", []),
                "alertas": validacion["flags"],
                "valido": validacion["valido"],
                "confianza": analisis.get("confianza", 0),
            }
            
            url_reporte = None
            try:
                ruta_pdf = self.reporter.generar_reporte(res_completo, doc_id)
                url_reporte = self.storage.subir_archivo(ruta_pdf, f"reporte_{doc_id}.pdf")
                os.remove(ruta_pdf)
                logger.info(f"PASO 6 (Report Generation) finalizado en {time.time() - inicio_paso:.2f}s | URL Reporte: {url_reporte}")
            except Exception as e:
                logger.error(f"PASO 6 (Report Generation) falló: {e}", exc_info=True)

            logger.info(f"Pipeline completo finalizado en {time.time() - inicio_total:.2f}s para {doc_id}")

            return {
                "doc_id": doc_id,
                "nombre_archivo": nombre,
                "url_blob": url_blob,
                "url_reporte": url_reporte,
                "num_paginas": extraccion["num_paginas"],
                "tipo_documento": analisis.get("tipo_documento"),
                "resumen": analisis.get("resumen"),
                "entidades": analisis.get("entidades", []),
                "alertas": validacion["flags"],
                "valido": validacion["valido"],
                "confianza": analisis.get("confianza", 0),
            }
        except Exception as e:
            logger.error(f"Error crítico en el pipeline para {doc_id}: {e}", exc_info=True)
            raise e

    def responder_pregunta(self, pregunta: str) -> dict:
        print(f"\n[Orchestrator] Pregunta: {pregunta}")
        respuesta = self.analyzer.responder_pregunta(pregunta)
        return {"respuesta": respuesta, "pregunta": pregunta}
