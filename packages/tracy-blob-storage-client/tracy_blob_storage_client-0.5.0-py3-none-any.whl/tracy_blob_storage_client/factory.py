import os
from typing import Optional
from .azure_blob import AzureBlobStorageClient
from .aws_blob import AWSBlobStorageClient
from .base import BlobStorageClient

def get_blob_storage_client(container_name: Optional[str] = None) -> BlobStorageClient:
    provider = os.getenv("BLOB_STORAGE_PROVIDER", "AWS").upper()
    if provider == "AZURE":
        return AzureBlobStorageClient(container_name)
    elif provider == "AWS":
        return AWSBlobStorageClient(container_name)
    else:
        raise ValueError(f"Unsupported BLOB_STORAGE_PROVIDER: {provider}")
