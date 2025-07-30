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
        pass

    @abstractmethod
    async def upload_blob(self, remote_dir: str, file_name: str, content: bytes) -> str:
        pass
