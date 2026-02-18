from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import Document, LedgerEntry, TradeTransaction, User
from backend.utils import get_current_user, hash_file
import os

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    doc_number: str = Form(...),
    doc_type: str = Form(...),
    seller_id: int = Form(...),
    currency: str = Form(...),
    amount: float = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1️⃣ Save file
    os.makedirs("files", exist_ok=True)
    file_path = f"files/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_hash = hash_file(file_path)

    # 2️⃣ Create Transaction (NEW – Step 2)
    tx = Transaction(
        buyer_id=current_user.id,
        seller_id=seller_id,
        currency=currency,
        amount=amount,
        status="PENDING"
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)

    # 3️⃣ Create Document
    document = Document(
        owner_id=current_user.id,
        doc_number=doc_number,
        doc_type=doc_type,
        transaction_id=tx.id,
        file_url=file.filename,
        hash=file_hash
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    # 4️⃣ Ledger entry
    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=current_user.id,
        action="ISSUED",
        metadata={"seller_id": seller_id}
    )
    session.add(ledger)
    session.commit()

    return {
        "message": "Document uploaded",
        "document_id": document.id,
        "transaction_id": tx.id
    }


@router.get("/")
def list_documents(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return session.exec(
        select(Document).where(Document.owner_id == current_user.id)
    ).all()


@router.get("/{document_id}")
def get_document(
    document_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    document = session.get(Document, document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document