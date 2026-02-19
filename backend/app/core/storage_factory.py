import os
from .storage_local import LocalStorage
from .storage_s3 import S3Storage


def get_storage():
    if os.getenv("STORAGE_MODE") == "S3":
        return S3Storage()
    return LocalStorage()
