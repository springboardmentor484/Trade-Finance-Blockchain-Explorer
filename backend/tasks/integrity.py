from backend.celery_app import celery
from backend.database import engine
from sqlmodel import Session
from backend.models import Document, Alert
from backend.utils import hash_file
import os


@celery.task
def verify_document_integrity(document_id: int):
    with Session(engine) as session:
        document = session.get(Document, document_id)

        if not document:
            return "Document not found"

        file_path = f"files/{document.file_url}"

        if not os.path.exists(file_path):
            return "File missing"

        new_hash = hash_file(file_path)

        if new_hash == document.hash:
            print(f"Document {document_id} integrity OK")
            return "Integrity OK"

        else:
            print(f"Document {document_id} integrity FAILED")

            # 🔥 CREATE ALERT
            alert = Alert(
                document_id=document.id,
                message="Hash mismatch detected"
            )
            session.add(alert)
            session.commit()

            return "Integrity FAILED - Alert created"