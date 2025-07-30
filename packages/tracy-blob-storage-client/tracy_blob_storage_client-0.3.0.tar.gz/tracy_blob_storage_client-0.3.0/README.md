# tracy-blob-storage-client

A unified async interface to upload and download blobs to/from **Azure Blob Storage** or **AWS S3/MinIO**, switchable via environment variable.

## Usage

```python
from tracy_blob_storage_client import get_blob_client

client = get_blob_client()

# download
await client.download_blob("some/key/file.bin", "/tmp")

# upload
await client.upload_blob("some/key", "file.bin", b"binary content")
