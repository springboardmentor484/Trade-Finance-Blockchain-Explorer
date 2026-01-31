from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlmodel import Session
from backend.database import get_session
from backend.models import Document, LedgerEntry
from backend.utils import get_current_user, hash_file
from backend.models import User
import os

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    doc_number: str = Form(...),
    doc_type: str = Form(...),
    seller_id: int = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    os.makedirs("files", exist_ok=True)

    file_path = f"files/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_hash = hash_file(file_path)

    document = Document(
        owner_id=current_user.id,
        doc_number=doc_number,
        doc_type=doc_type,
        file_url=file.filename,
        hash=file_hash
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=current_user.id,
        action="ISSUED",
        metadata={"seller_id": seller_id}
    )
    session.add(ledger)
    session.commit()

    return {"message": "Document uploaded", "document_id": document.id}

from sqlmodel import select


@router.get("/")
def list_documents(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    documents = session.exec(
        select(Document).where(Document.owner_id == current_user.id)
    ).all()

    return documents