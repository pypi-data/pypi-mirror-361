import os
import logging
import aioboto3
import aiofiles
from .base import BlobStorageClient

class AWSBlobStorageClient(BlobStorageClient):
    def __init__(self):
        self.bucket_name = os.getenv("BLOB_STORAGE_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.endpoint_url = os.getenv("BLOB_STORAGE_ENDPOINT_URL")
        self.session = aioboto3.Session()

    async def download_blob(self, remote_path: str, local_dir: str) -> str:
        file_name = os.path.basename(remote_path)
        local_path = os.path.join(local_dir, file_name)

        async with self.session.client("s3", region_name=self.region, endpoint_url=self.endpoint_url) as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket_name, Key=remote_path)
                content = await response["Body"].read()
                async with aiofiles.open(local_path, "wb") as f:
                    await f.write(content)
                logging.info(f"Downloaded {remote_path} to {local_path}")
                return local_path
            except Exception as e:
                logging.error(f"Error downloading {remote_path}: {e}")
                raise

    async def upload_blob(self, remote_dir: str, file_name: str, content: bytes) -> str:
        blob_path = f"{remote_dir.strip('/')}/{file_name}"
        async with self.session.client("s3", region_name=self.region, endpoint_url=self.endpoint_url) as s3:
            try:
                await s3.put_object(Bucket=self.bucket_name, Key=blob_path, Body=content)
                logging.info(f"Uploaded {blob_path}")
                return blob_path
            except Exception as e:
                logging.error(f"Error uploading {blob_path}: {e}")
                raise
