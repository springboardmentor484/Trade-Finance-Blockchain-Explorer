from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import LedgerEntry
from backend.utils import get_current_user
from backend.models import User

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("/")
def get_all_ledger_entries(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return session.exec(select(LedgerEntry)).all()


@router.get("/{document_id}")
def get_ledger_for_document(
    document_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return session.exec(
        select(LedgerEntry).where(LedgerEntry.document_id == document_id)
    ).all()

@router.post("/")
def create_ledger_entry(
    document_id: int,
    action: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1️⃣ Get document
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 2️⃣ Create ledger entry
    entry = LedgerEntry(
        document_id=document_id,
        actor=current_user.email,
        action=action,
    )

    session.add(entry)

    # 3️⃣ AUTO UPDATE TRANSACTION STATUS (STEP 6)
    if document.transaction_id:
        transaction = session.get(TradeTransaction, document.transaction_id)

        if transaction:
            if action == "DOCUMENT_UPLOADED":
                transaction.status = TransactionStatus.in_progress

            elif action == "SHIPPED":
                transaction.status = TransactionStatus.in_progress

            elif action == "PAID":
                transaction.status = TransactionStatus.completed

            elif action == "DISPUTE":
                transaction.status = TransactionStatus.disputed

            transaction.updated_at = datetime.utcnow()
            session.add(transaction)

    session.commit()
    session.refresh(entry)

    return entry