import os
import logging
import aiofiles
from azure.storage.blob.aio import BlobServiceClient
from .base import BlobStorageClient

class AzureBlobStorageClient(BlobStorageClient):
    def __init__(self):
        self.connection_string = os.getenv("BLOB_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("BLOB_STORAGE_CONTAINER_NAME")
        self.client = BlobServiceClient.from_connection_string(self.connection_string)

    async def download_blob(self, remote_path: str, local_dir: str) -> str:
        file_name = os.path.basename(remote_path)
        local_path = os.path.join(local_dir, file_name)

        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(remote_path)
            stream = await blob_client.download_blob()
            content = await stream.readall()
            async with aiofiles.open(local_path, "wb") as f:
                await f.write(content)
            logging.info(f"Downloaded {remote_path} to {local_path}")
            return local_path
        except Exception as e:
            logging.error(f"Error downloading {remote_path}: {e}")
            raise

    async def upload_blob(self, remote_dir: str, file_name: str, content: bytes) -> str:
        blob_path = f"{remote_dir.strip('/')}/{file_name}"
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_path)
            await blob_client.upload_blob(content, overwrite=True)
            logging.info(f"Uploaded {blob_path}")
            return blob_path
        except Exception as e:
            logging.error(f"Error uploading {blob_path}: {e}")
            raise
