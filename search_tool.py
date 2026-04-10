import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import OpenAI


class SearchTool:
    def __init__(self):
        self.oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            index_name=os.getenv("AZURE_SEARCH_INDEX"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")),
        )
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    def _obtener_embedding(self, texto: str) -> list[float]:
        texto = texto[:8000]
        response = self.oai.embeddings.create(input=texto, model=self.embedding_model)
        return response.data[0].embedding

    def indexar_documento(self, doc_id: str, contenido: str, tipo_doc: str, nombre_archivo: str) -> bool:
        try:
            embedding = self._obtener_embedding(contenido)
            documento = {
                "id": doc_id,
                "contenido": contenido[:32000],
                "tipo_doc": tipo_doc,
                "nombre_archivo": nombre_archivo,
                "fecha_subida": __import__("datetime").datetime.utcnow().isoformat(),
                "vector_contenido": embedding,
            }
            self.client.upload_documents(documents=[documento])
            return True
        except Exception as e:
            print(f"Error indexando: {e}")
            return False

    def buscar_similares(self, consulta: str, top: int = 3) -> list[dict]:
        try:
            embedding_consulta = self._obtener_embedding(consulta)
            vector_query = VectorizedQuery(
                vector=embedding_consulta,
                k_nearest_neighbors=top,
                fields="vector_contenido",
            )
            resultados = self.client.search(
                search_text=consulta,
                vector_queries=[vector_query],
                select=["id", "contenido", "tipo_doc", "nombre_archivo", "fecha_subida"],
                top=top,
            )
            return [r for r in resultados]
        except Exception as e:
            print(f"Error buscando: {e}")
            return []
