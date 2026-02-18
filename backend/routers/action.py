from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import Document, LedgerEntry, User
from backend.utils import get_current_user
from backend.utils import is_action_allowed


from backend.models import TradeTransaction
import uuid

router = APIRouter(prefix="/actions", tags=["Actions"])

@router.post("/{document_id}/{action}")
def perform_action(
    document_id: int,
    action: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    document = session.exec(
        select(Document).where(Document.id == document_id)
    ).first()

    if not document:
        raise HTTPException(404, "Document not found")

    last_entry = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.document_id == document_id)
        .order_by(LedgerEntry.id.desc())
    ).first()

    last_action = last_entry.action if last_entry else "ISSUED"

    if not is_action_allowed(
        document.doc_type,
        last_action,
        current_user.role,
        action
    ):
        raise HTTPException(403, "Action not allowed")

    # STEP 2A: AUTO-CREATE LOC
    if action == "ISSUE_LOC" and document.doc_type == "PO":
        loc_doc = Document(
            owner_id=current_user.id,
            doc_type="LOC",
            doc_number=f"LOC-{uuid.uuid4().hex[:8]}",
            transaction_id=document.transaction_id,
            file_url=None,
            hash=None
        )
        session.add(loc_doc)
        session.commit()
        session.refresh(loc_doc)

        loc_ledger = LedgerEntry(
            document_id=loc_doc.id,
            actor_id=current_user.id,
            action="ISSUED"
        )
        session.add(loc_ledger)

    # STEP 2B: ORIGINAL LEDGER ENTRY
    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=current_user.id,
        action=action
    )
    session.add(ledger)
    session.commit()

    return {"status": "SUCCESS", "action": action}
