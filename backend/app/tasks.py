import os
import hashlib
from sqlmodel import Session, select
from app.database import engine
from app.models import Document, RiskScore, AuditLog, User
from app.celery_app import celery_app


def calculate_file_hash(file_path: str) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        sha.update(f.read())
    return sha.hexdigest()


@celery_app.task
def test_task():
    print("✅ Celery is working!")
    return "OK"


@celery_app.task
def integrity_check_job():
    print("🔍 Running integrity check job...")

    with Session(engine) as session:
        documents = session.exec(select(Document)).all()

        for doc in documents:
            file_path = f"files/{doc.file_url}"

            if not os.path.exists(file_path):
                print(f"❌ File missing for document {doc.id}")
                continue

            current_hash = calculate_file_hash(file_path)

            if current_hash != doc.file_hash:
                print(f"⚠️ Hash mismatch detected for document {doc.id}")

                # 1️⃣ Flag document
                doc.is_compromised = True
                session.add(doc)

                # 2️⃣ Update RiskScore of owner
                risk = session.exec(
                    select(RiskScore).where(RiskScore.user_id == doc.owner_id)
                ).first()

                if not risk:
                    risk = RiskScore(
                        user_id=doc.owner_id,
                        score=50,
                        rationale="Initial integrity violation detected"
                    )
                else:
                    risk.score += 10
                    risk.rationale = "Repeated integrity violations detected"

                session.add(risk)

                # 3️⃣ Create AuditLog (system-triggered)
                audit = AuditLog(
                    admin_id=doc.owner_id,  # system placeholder
                    action="INTEGRITY_MISMATCH",
                    target_type="DOCUMENT",
                    target_id=doc.id
                )

                session.add(audit)

            else:
                doc.is_compromised = False
                session.add(doc)

        session.commit()

    print("✅ Integrity check completed")
