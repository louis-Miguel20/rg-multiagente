import os
import json
from openai import OpenAI
from tools.search_tool import SearchTool


class AnalyzerAgent:
    """
    Agente 2: Analiza el documento con GPT-4o.
    Usa RAG: busca documentos similares para enriquecer el contexto.
    """

    PROMPT_ANALISIS = """Eres un analista experto en documentos empresariales en español e inglés.

Contexto de documentos similares ya procesados:
{contexto}

Documento a analizar:
{texto}

Extrae la siguiente información y responde ÚNICAMENTE con JSON válido, sin texto adicional:
{{
  "tipo_documento": "contrato | factura | reporte | otro",
  "resumen": "Resumen ejecutivo en 2-3 oraciones",
  "entidades": [
    {{"nombre": "nombre del campo", "tipo": "fecha | monto | parte | plazo | otro", "valor": "valor extraído"}}
  ],
  "alertas": ["lista de cláusulas riesgosas, montos altos, vencimientos próximos, o anomalías"],
  "confianza": 0.95
}}"""

    def __init__(self):
        self.oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.modelo = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.search = SearchTool()

    def analizar(self, texto: str) -> dict:
        print(f"[AnalyzerAgent] Analizando ({len(texto)} caracteres)...")

        docs_similares = self.search.buscar_similares(texto[:500], top=2)
        contexto = "\n---\n".join(
            d.get("contenido", "")[:400] for d in docs_similares
        ) if docs_similares else "Sin documentos previos para comparar."

        prompt = self.PROMPT_ANALISIS.format(
            contexto=contexto,
            texto=texto[:4000],
        )

        respuesta = self.oai.chat.completions.create(
            model=self.modelo,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        contenido = respuesta.choices[0].message.content
        try:
            return json.loads(contenido)
        except json.JSONDecodeError:
            return {
                "tipo_documento": "otro",
                "resumen": "No se pudo analizar el documento.",
                "entidades": [],
                "alertas": ["Error al parsear respuesta del modelo"],
                "confianza": 0.0,
            }

    def responder_pregunta(self, pregunta: str) -> str:
        print(f"[AnalyzerAgent] Pregunta: {pregunta}")

        fragmentos = self.search.buscar_similares(pregunta, top=4)
        if not fragmentos:
            return "No se encontraron documentos relevantes para responder la pregunta."

        contexto = "\n---\n".join(f["contenido"][:600] for f in fragmentos)

        prompt = f"""Responde la pregunta basándote ÚNICAMENTE en los documentos proporcionados.
Si la información no está disponible, responde exactamente: "No encontrado en los documentos cargados."

Pregunta: {pregunta}

Documentos:
{contexto}

Respuesta concisa y directa:"""

        respuesta = self.oai.chat.completions.create(
            model=self.modelo,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return respuesta.choices[0].message.content
