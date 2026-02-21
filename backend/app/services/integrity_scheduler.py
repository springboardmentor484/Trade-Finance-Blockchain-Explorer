import os
import hashlib
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select

from ..db import engine
from ..models import Document, LedgerEntry, DocumentStatus


FILES_DIR = "uploaded_files"

scheduler = BackgroundScheduler()


def verify_all_documents():
    """
    Automatic integrity verification.
    Runs periodically and records tampering in ledger.
    """
    with Session(engine) as session:
        documents = session.exec(select(Document)).all()

        for doc in documents:
            filepath = os.path.join(FILES_DIR, doc.file_url)

            if not os.path.exists(filepath):
                continue

            with open(filepath, "rb") as f:
                content = f.read()

            computed_hash = hashlib.sha256(content).hexdigest()

            is_valid = computed_hash == doc.hash

            # Only log if tampered OR periodic verification log needed
            ledger = LedgerEntry(
                document_id=doc.id,
                actor_id=None,  # system action
                action="AUTO_VERIFY",
                meta={
                    "verification_time": str(datetime.utcnow()),
                    "stored_hash": doc.hash,
                    "computed_hash": computed_hash,
                    "result": "PASSED" if is_valid else "FAILED",
                    "auto": True,
                },
            )

            session.add(ledger)

        session.commit()


def start_integrity_scheduler():
    """
    Start scheduler to run every 5 minutes.
    """
    scheduler.add_job(
        verify_all_documents,
        "interval",
        minutes=5,
        id="document_integrity_job",
        replace_existing=True,
    )

    scheduler.start()
