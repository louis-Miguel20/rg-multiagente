import os
from azure.storage.blob import BlobServiceClient


class StorageTool:
    def __init__(self):
        self.service = BlobServiceClient.from_connection_string(
            os.getenv("AZURE_STORAGE_CONNECTION")
        )
        self.container = os.getenv("AZURE_STORAGE_CONTAINER", "documentos")
        self._crear_container_si_no_existe()

    def _crear_container_si_no_existe(self):
        try:
            self.service.create_container(self.container)
        except Exception:
            pass

    def subir_archivo(self, ruta_local: str, nombre_blob: str) -> str:
        blob_client = self.service.get_blob_client(container=self.container, blob=nombre_blob)
        with open(ruta_local, "rb") as f:
            blob_client.upload_blob(f, overwrite=True)
        return blob_client.url
