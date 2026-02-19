from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):

    @abstractmethod
    def upload(self, file_data: bytes, filename: str, content_type: str) -> str:
        pass

    @abstractmethod
    def delete(self, filename: str) -> None:
        pass
