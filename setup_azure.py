"""
PASO 1: Ejecutar este script UNA SOLA VEZ para crear el índice en Azure AI Search.
Comando: python setup_azure.py
"""
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SimpleField,
    SearchableField,
)

load_dotenv()

def crear_indice():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")

    client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="contenido", type=SearchFieldDataType.String, analyzer_name="es.lucene"),
        SimpleField(name="tipo_doc", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="nombre_archivo", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="fecha_subida", type=SearchFieldDataType.String, filterable=True),
        SearchField(
            name="vector_contenido",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="perfil-hnsw",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-config")],
        profiles=[VectorSearchProfile(name="perfil-hnsw", algorithm_configuration_name="hnsw-config")],
    )

    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)

    try:
        client.delete_index(index_name)
        print(f"Índice anterior '{index_name}' eliminado.")
    except Exception:
        pass

    result = client.create_index(index)
    print(f"✅ Índice '{result.name}' creado correctamente con soporte de vectores.")

if __name__ == "__main__":
    crear_indice()
