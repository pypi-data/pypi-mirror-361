import pytest

@pytest.mark.asyncio
async def test_azure_upload_and_exists_and_fetch(azure_client, tmp_path, monkeypatch):
    # You’ll need a running Azurite or actual Azure account; here’s pattern
    data = b"goodbye"
    key = "path/to/data.txt"

    # upload
    blob_path = await azure_client.upload_blob("path/to/data.txt", data)
    assert blob_path.endswith("data.txt")

    # exists
    exists = await azure_client.blob_exists(key)
    assert exists is True

    # fetch content
    content = await azure_client.fetch_blob_content(key)
    assert content == data.decode("utf-8")
