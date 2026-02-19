from celery import Celery

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

from backend.database import get_session
from backend.models import Document, Alert
from backend.utils import hash_file
import os


@celery.task
def check_integrity(document_id: int):
    session = SessionLocal()

    document = session.get(Document, document_id)

    if not document:
        return "Document not found"

    file_path = document.file_url  # adjust if needed

    if not os.path.exists(file_path):
        return "File missing"

    recalculated_hash = hash_file(file_path)

    if recalculated_hash != document.hash:
        alert = Alert(
            document_id=document.id,
            message="Hash mismatch detected!"
        )
        session.add(alert)
        session.commit()

        return "Integrity violation detected"

    return "Integrity verified"