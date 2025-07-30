from abc import ABC, abstractmethod

class BlobStorageClient(ABC):
    @abstractmethod
    async def download_blob(self, remote_path: str, local_dir: str) -> str:
        pass

    @abstractmethod
    async def upload_blob(self, remote_dir: str, file_name: str, content: bytes) -> str:
        pass
