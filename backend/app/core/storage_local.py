import os
from pathlib import Path
from .storage import StorageProvider

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)


class LocalStorage(StorageProvider):

    def upload(self, file_data: bytes, filename: str, content_type: str) -> str:
        file_path = UPLOAD_DIR / filename

        with open(file_path, "wb") as f:
            f.write(file_data)

        return f"/uploads/{filename}"

    def delete(self, filename: str) -> None:
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            os.remove(file_path)
