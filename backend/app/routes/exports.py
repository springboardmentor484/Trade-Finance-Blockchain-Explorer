from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from io import StringIO, BytesIO
import csv
import hashlib
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from ..db import get_session
from ..models import (
    TradeTransaction,
    LedgerEntry,
    RiskScore,
    UserRole,
)

# 🔐 KEEP THIS (used internally by require_action)
from ..dependencies.auth import get_current_user

# 🔐 NEW SECURITY IMPORTS
from ..security.permission import require_action
from ..security.role_matrix import Action

router = APIRouter(prefix="/exports", tags=["Exports"])


# =====================================================
# GENERIC CSV HELPER
# =====================================================

def stream_csv(headers: list, rows: list, filename: str):
    def generate():
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(headers)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        for row in rows:
            writer.writerow(row)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )


# =====================================================
# CSV EXPORT — TRANSACTIONS
# =====================================================

@router.get("/transactions/csv")
def export_transactions_csv(
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_action(Action.EXPORT_TRANSACTIONS)),
):
    role = current_user["role"]
    user_id = current_user["user_id"]

    query = select(TradeTransaction)

    if role != UserRole.ADMIN.value:
        query = query.where(
            (TradeTransaction.buyer_id == user_id)
            | (TradeTransaction.seller_id == user_id)
            | (TradeTransaction.lc_issuer_id == user_id)
        )

    transactions = session.exec(query).all()

    headers = [
        "ID", "Buyer", "Seller", "Amount",
        "Currency", "Status", "Created At"
    ]

    rows = [
        [
            t.id,
            t.buyer_id,
            t.seller_id,
            t.amount,
            t.currency,
            t.status.value,
            t.created_at,
        ]
        for t in transactions
    ]

    filename = f"transactions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return stream_csv(headers, rows, filename)


# =====================================================
# CSV EXPORT — LEDGER
# =====================================================

@router.get("/ledger/csv")
def export_ledger_csv(
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_action(Action.EXPORT_LEDGER)),
):
    role = current_user["role"]
    user_id = current_user["user_id"]

    query = select(LedgerEntry)

    if role != UserRole.ADMIN.value:
        query = query.where(LedgerEntry.actor_id == user_id)

    entries = session.exec(query).all()

    headers = ["ID", "Document ID", "Actor ID", "Action", "Timestamp"]

    rows = [
        [
            e.id,
            e.document_id,
            e.actor_id,
            e.action,
            e.timestamp,
        ]
        for e in entries
    ]

    filename = f"ledger_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return stream_csv(headers, rows, filename)


# =====================================================
# PDF EXPORT — FULL TRANSACTION REPORT
# =====================================================

@router.get("/transactions/{transaction_id}/pdf")
def export_transaction_pdf(
    transaction_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_action(Action.EXPORT_PDF)),
):
    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Additional ownership validation
    if (
        current_user["role"] != UserRole.ADMIN.value
        and current_user["user_id"] not in [
            transaction.buyer_id,
            transaction.seller_id,
            transaction.lc_issuer_id,
        ]
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    risk = session.exec(
        select(RiskScore).where(RiskScore.transaction_id == transaction_id)
    ).first()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Trade Transaction Report</b>", styles["Title"]))
    elements.append(Spacer(1, 15))

    data = [
        ["Transaction ID", transaction.id],
        ["Buyer ID", transaction.buyer_id],
        ["Seller ID", transaction.seller_id],
        ["Amount", f"{transaction.amount} {transaction.currency}"],
        ["Status", transaction.status.value],
        ["Created At", str(transaction.created_at)],
    ]

    if risk:
        data.append(["Risk Score", risk.score])
        data.append(["Risk Factors", str(risk.factors)])

    table = Table(data, colWidths=[160, 320])
    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])

    elements.append(table)
    elements.append(Spacer(1, 25))

    # Integrity Hash (audit proof)
    raw_string = f"{transaction.id}{transaction.amount}{transaction.status}"
    integrity_hash = hashlib.sha256(raw_string.encode()).hexdigest()

    elements.append(
        Paragraph(f"Integrity Hash: {integrity_hash}", styles["Normal"])
    )

    elements.append(
        Paragraph(
            f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            styles["Normal"],
        )
    )

    doc.build(elements)
    buffer.seek(0)

    filename = f"transaction_{transaction_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )
