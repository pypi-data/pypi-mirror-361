# tests/test_aws_blob_errors.py
import os
import pytest
from tracy_blob_storage_client.aws_blob import AWSBlobStorageClient

@pytest.mark.parametrize("arg_value, env_value", [
    (None, None),                  # neither provided
    ("", ""),                      # empty strings
])
def test_aws_init_missing_container(arg_value, env_value, monkeypatch):
    # Ensure env var is unset or empty
    monkeypatch.delenv("BLOB_STORAGE_CONTAINER", raising=False)
    if env_value is not None:
        monkeypatch.setenv("BLOB_STORAGE_CONTAINER", env_value)

    # Now __init__ should blow up
    with pytest.raises(ValueError) as exc:
        AWSBlobStorageClient(container_name=arg_value)
    assert "container_name" in str(exc.value) or "bucket_name" in str(exc.value)
