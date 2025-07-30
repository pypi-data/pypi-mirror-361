import pytest
import asyncio

@pytest.mark.asyncio
async def test_aws_upload_and_exists_and_fetch(aws_client, tmp_path):
    data = b"hello world"
    key = "folder/hello.txt"

    # upload
    blob_path = await aws_client.upload_blob("folder/hello.txt", data)
    assert blob_path == key

    # exists
    exists = await aws_client.blob_exists(key)
    assert exists is True

    # fetch content
    content = await aws_client.fetch_blob_content(key)
    assert content == data.decode("utf-8")
