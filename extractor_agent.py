import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest


class ExtractorAgent:
    """
    Agente 1: Extrae texto, tablas y pares clave-valor de cualquier PDF/imagen.
    Usa: azure-ai-documentintelligence==1.0.2 (NO el deprecated azure-ai-formrecognizer).
    """

    def __init__(self):
        self.client = DocumentIntelligenceClient(
            endpoint=os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("DOCUMENTINTELLIGENCE_API_KEY")),
        )

    def extraer(self, ruta_archivo: str) -> dict:
        print(f"[ExtractorAgent] Extrayendo: {ruta_archivo}")

        with open(ruta_archivo, "rb") as f:
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-layout",
                body=f,
            )

        resultado = poller.result()

        texto_completo = ""
        if resultado.paragraphs:
            texto_completo = "\n".join(p.content for p in resultado.paragraphs)

        tablas = []
        if resultado.tables:
            for tabla in resultado.tables:
                filas = {}
                for celda in tabla.cells:
                    fila = celda.row_index
                    if fila not in filas:
                        filas[fila] = []
                    filas[fila].append(celda.content)
                tablas.append(list(filas.values()))

        return {
            "texto": texto_completo,
            "tablas": tablas,
            "num_paginas": len(resultado.pages) if resultado.pages else 0,
            "tiene_texto": len(texto_completo.strip()) > 0,
        }
