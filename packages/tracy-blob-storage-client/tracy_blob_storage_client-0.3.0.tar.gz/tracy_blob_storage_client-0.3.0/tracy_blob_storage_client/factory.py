import os
from .azure_blob import AzureBlobStorageClient
from .aws_blob import AWSBlobStorageClient
from .base import BlobStorageClient

def get_blob_storage_client() -> BlobStorageClient:
    provider = os.getenv("BLOB_STORAGE_PROVIDER", "AWS").upper()
    if provider == "AZURE":
        return AzureBlobStorageClient()
    elif provider == "AWS":
        return AWSBlobStorageClient()
    else:
        raise ValueError(f"Unsupported BLOB_STORAGE_PROVIDER: {provider}")
