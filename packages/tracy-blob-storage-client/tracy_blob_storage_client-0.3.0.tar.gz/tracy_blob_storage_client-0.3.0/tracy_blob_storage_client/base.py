from abc import ABC, abstractmethod
from typing import Optional
import os

class BlobStorageClient(ABC):    
    def __init__(self, container_name: Optional[str] = None):        
        # if the user passed a name, use it; otherwise pull from the env var
        self.container_name = container_name or os.getenv("BLOB_STORAGE_CONTAINER")
        if not self.container_name:
            raise ValueError("container_name must be provided either as an argument or in BLOB_STORAGE_CONTAINER")
        
    @abstractmethod
    async def download_blob(self, remote_path: str, local_dir: str) -> str:
        """
        Download blob to a local path
        """
        pass

    @abstractmethod
    async def upload_blob(self, remote_dir: str, file_name: str, content: bytes) -> str:
        """
        Upload blob content to a remote path
        """
        pass

    @abstractmethod
    async def blob_exists(self, remote_path: str) -> bool:
        """
        Return True if the object/blob exists at `remote_path`
        """
        ...

    @abstractmethod
    async def fetch_blob_content(self, remote_path: str) -> str:
        """
        Return the blob's content as a UTF-8 string
        """
        ...

    async def close(self):
        """
        Optional: clean up underlying client resources.
        Default no-op.
        """
        pass
