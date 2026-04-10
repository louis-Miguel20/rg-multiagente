import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agents.extractor_agent import ExtractorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.validator_agent import ValidatorAgent
from tools.search_tool import SearchTool
from tools.storage_tool import StorageTool


class Orchestrator:
    """
    Orquestador central: coordina el flujo completo de 4 agentes.
    Cada agente es independiente y reemplazable.
    """

    def __init__(self):
        self.extractor = ExtractorAgent()
        self.analyzer = AnalyzerAgent()
        self.validator = ValidatorAgent()
        self.search = SearchTool()
        self.storage = StorageTool()

    def procesar_documento(self, ruta_archivo: str) -> dict:
        nombre = Path(ruta_archivo).name
        doc_id = str(uuid.uuid4())

        print(f"\n{'='*50}")
        print(f"[Orchestrator] Iniciando pipeline: {nombre}")
        print(f"[Orchestrator] ID: {doc_id}")
        print(f"{'='*50}")

        # PASO 1: Subir a Blob Storage
        try:
            url_blob = self.storage.subir_archivo(ruta_archivo, f"{doc_id}_{nombre}")
            print(f"[Orchestrator] ✅ Subido a Blob: {url_blob}")
        except Exception as e:
            print(f"[Orchestrator] ⚠️ Blob Storage no disponible: {e}")
            url_blob = None

        # PASO 2: Extraer contenido con Document Intelligence
        extraccion = self.extractor.extraer(ruta_archivo)
        print(f"[Orchestrator] ✅ Extracción: {extraccion['num_paginas']} páginas")

        if not extraccion["tiene_texto"]:
            return {
                "error": "El documento no contiene texto legible.",
                "doc_id": doc_id,
            }

        # PASO 3: Analizar con GPT-4o + RAG
        analisis = self.analyzer.analizar(extraccion["texto"])
        print(f"[Orchestrator] ✅ Análisis: tipo={analisis.get('tipo_documento')}, confianza={analisis.get('confianza')}")

        # PASO 4: Validar contra reglas de negocio
        validacion = self.validator.validar(analisis)
        print(f"[Orchestrator] ✅ Validación: válido={validacion['valido']}, flags={validacion['total_alertas']}")

        # PASO 5: Indexar en Azure AI Search
        self.search.indexar_documento(
            doc_id=doc_id,
            contenido=extraccion["texto"],
            tipo_doc=analisis.get("tipo_documento", "otro"),
            nombre_archivo=nombre,
        )
        print(f"[Orchestrator] ✅ Indexado en AI Search")

        return {
            "doc_id": doc_id,
            "nombre_archivo": nombre,
            "url_blob": url_blob,
            "num_paginas": extraccion["num_paginas"],
            "tipo_documento": analisis.get("tipo_documento"),
            "resumen": analisis.get("resumen"),
            "entidades": analisis.get("entidades", []),
            "alertas": validacion["flags"],
            "valido": validacion["valido"],
            "confianza": analisis.get("confianza", 0),
        }

    def responder_pregunta(self, pregunta: str) -> dict:
        print(f"\n[Orchestrator] Pregunta: {pregunta}")
        respuesta = self.analyzer.responder_pregunta(pregunta)
        return {"respuesta": respuesta, "pregunta": pregunta}
