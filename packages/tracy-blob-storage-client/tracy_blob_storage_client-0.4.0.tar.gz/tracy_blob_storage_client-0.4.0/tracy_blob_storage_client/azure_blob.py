import os
import logging
from typing import Optional, Union
import uuid
import aiofiles
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from .base import BlobStorageClient

class AzureBlobStorageClient(BlobStorageClient):
    def __init__(self, container_name: Optional[str] = None):
        super().__init__(container_name=container_name)
        self.connection_string = os.getenv("BLOB_STORAGE_CONNECTION_STRING")        
        self.client = BlobServiceClient.from_connection_string(self.connection_string)

    async def download_blob(self, remote_path: str, local_dir: str, make_unique=False) -> str:
        file_name = os.path.basename(remote_path)
        if make_unique:
            filename = f"{uuid.uuid4()}_{filename}"
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

    async def upload_blob(self, remote_path: str, content: Union[str, bytes]) -> str:         
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(remote_path)
            await blob_client.upload_blob(content, overwrite=True)
            logging.info(f"Uploaded {remote_path}")
            return remote_path
        except Exception as e:
            logging.error(f"Error uploading {remote_path}: {e}")
            raise

    async def blob_exists(self, remote_path: str) -> bool:
        try:
            container = self.client.get_container_client(self.container_name)
            blob = container.get_blob_client(remote_path)
            return await blob.exists()
        except Exception as e:
            logging.error(f"Error checking blob exists: {e}")
            return False

    async def fetch_blob_content(self, remote_path: str) -> str:
        container = self.client.get_container_client(self.container_name)
        blob = container.get_blob_client(remote_path)

        try:
            stream = await blob.download_blob()
            data = await stream.readall()
            return data.decode("utf-8")
        except ResourceNotFoundError:
            logging.error(f"Blob not found: {remote_path}")
            raise
        except Exception as e:
            logging.error(f"Error fetching blob content: {e}")
            raise

    async def close(self):
        await self.client.close()

