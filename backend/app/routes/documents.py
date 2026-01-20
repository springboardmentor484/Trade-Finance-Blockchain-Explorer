from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db import get_session
from app.models import Document, LedgerEntry, DocumentStatus, UserRole
from app.schemas.document import DocumentCreate, DocumentAction
from app.rules.document_rules import validate_transition

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/")
def create_document(
    payload: DocumentCreate,
    user_id: int = Query(...),
    session: Session = Depends(get_session),
):
    document = Document(
        doc_type=payload.doc_type,
        doc_number=payload.doc_number,
        owner_id=user_id,
        file_url=payload.file_url,
        hash=payload.hash,
        status=DocumentStatus.ISSUED,
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    session.add(
        LedgerEntry(
            document_id=document.id,
            actor_id=user_id,
            action=DocumentStatus.ISSUED.value,
            meta={"event": "Document issued"},
        )
    )
    session.commit()

    return {"id": document.id, "status": document.status}


@router.get("/{doc_id}")
def get_document(doc_id: int, session: Session = Depends(get_session)):
    doc = session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/{doc_id}/action")
def perform_action(
    doc_id: int,
    payload: DocumentAction,
    user_id: int = Query(...),
    session: Session = Depends(get_session),
):
    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    user_role = UserRole.BUYER  # TEMP (JWT later)

    try:
        validate_transition(
            role=user_role,
            current_status=document.status,
            next_status=payload.action,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    document.status = payload.action
    session.add(document)

    session.add(
        LedgerEntry(
            document_id=doc_id,
            actor_id=user_id,
            action=payload.action.value,
            meta=payload.meta,
        )
    )

    session.commit()

    return {
        "message": "Action recorded",
        "new_status": payload.action,
    }


@router.get("/{doc_id}/ledger")
def get_ledger(doc_id: int, session: Session = Depends(get_session)):
    return session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.document_id == doc_id)
        .order_by(LedgerEntry.id)
    ).all()
