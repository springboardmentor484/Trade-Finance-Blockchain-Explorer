"""
Analytics and Reporting endpoints for Module E
Provides document/transaction analytics, exports, and KPIs
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from io import StringIO
import csv
import os
import hashlib

from ..db import get_session
from ..models import (
    Document,
    DocumentStatus,
    TradeTransaction,
    TransactionStatus,
    User,
    LedgerEntry,
)
from ..dependencies.auth import get_current_user
from ..rules.transaction_rules import get_risk_level

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# -------------------------
# DOCUMENT ANALYTICS
# -------------------------
@router.get("/documents/summary")
def get_document_analytics(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get document analytics for the current user"""
    user_id = current_user["user_id"]

    # Total documents
    total_docs = session.exec(
        select(func.count(Document.id)).where(Document.owner_id == user_id)
    ).one()

    # Documents by status
    status_breakdown = {}
    for status in DocumentStatus:
        count = session.exec(
            select(func.count(Document.id)).where(
                (Document.owner_id == user_id) & (Document.status == status)
            )
        ).one()
        status_breakdown[status.value] = count

    # Recent documents
    recent_docs = session.exec(
        select(Document)
        .where(Document.owner_id == user_id)
        .order_by(Document.created_at.desc())
        .limit(5)
    ).all()

    return {
        "user_id": user_id,
        "total_documents": total_docs,
        "status_breakdown": status_breakdown,
        "recent_documents": [
            {
                "id": d.id,
                "doc_number": d.doc_number,
                "doc_type": d.doc_type.value,
                "status": d.status.value,
                "created_at": d.created_at,
            }
            for d in recent_docs
        ],
    }


# -------------------------
# TRANSACTION ANALYTICS
# -------------------------
@router.get("/transactions/summary")
def get_transaction_analytics(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get transaction analytics and KPIs"""
    user_id = current_user["user_id"]

    # Get user's transactions
    transactions = session.exec(
        select(TradeTransaction).where(
            (TradeTransaction.buyer_id == user_id)
            | (TradeTransaction.seller_id == user_id)
            | (TradeTransaction.lc_issuer_id == user_id)
        )
    ).all()

    if not transactions:
        return {
            "user_id": user_id,
            "total_transactions": 0,
            "total_volume": 0.0,
            "average_transaction": 0.0,
            "status_breakdown": {},
            "currency_breakdown": {},
            "average_risk_score": 0.0,
            "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
        }

    # Calculate metrics
    total_volume = sum(t.amount for t in transactions)
    avg_transaction = total_volume / len(transactions) if transactions else 0

    # Status breakdown
    status_breakdown = {}
    for status in TransactionStatus:
        count = sum(1 for t in transactions if t.status == status)
        if count > 0:
            status_breakdown[status.value] = count

    # Currency breakdown
    currency_breakdown = {}
    for tx in transactions:
        if tx.currency not in currency_breakdown:
            currency_breakdown[tx.currency] = 0
        currency_breakdown[tx.currency] += tx.amount

    # Risk analysis
    avg_risk = sum(t.risk_score for t in transactions) / len(transactions)
    risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for tx in transactions:
        level = get_risk_level(tx.risk_score)
        risk_dist[level] += 1

    return {
        "user_id": user_id,
        "total_transactions": len(transactions),
        "total_volume": round(total_volume, 2),
        "average_transaction": round(avg_transaction, 2),
        "status_breakdown": status_breakdown,
        "currency_breakdown": currency_breakdown,
        "average_risk_score": round(avg_risk, 2),
        "risk_distribution": risk_dist,
    }


# -------------------------
# EXPORT ENDPOINTS
# -------------------------
@router.get("/export/documents/csv")
def export_documents_csv(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Export user's documents as CSV"""
    user_id = current_user["user_id"]

    documents = session.exec(
        select(Document)
        .where(Document.owner_id == user_id)
        .order_by(Document.created_at.desc())
    ).all()

    # Create CSV
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "ID",
            "Doc Number",
            "Type",
            "Status",
            "File URL",
            "Hash",
            "Created At",
        ],
    )

    writer.writeheader()
    for doc in documents:
        writer.writerow(
            {
                "ID": doc.id,
                "Doc Number": doc.doc_number,
                "Type": doc.doc_type.value,
                "Status": doc.status.value,
                "File URL": doc.file_url,
                "Hash": doc.hash[:16] + "...",  # Truncate for readability
                "Created At": doc.created_at.isoformat(),
            }
        )

    return {
        "filename": f"documents_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
        "content": output.getvalue(),
        "record_count": len(documents),
    }


@router.get("/export/transactions/csv")
def export_transactions_csv(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Export user's transactions as CSV"""
    user_id = current_user["user_id"]

    transactions = session.exec(
        select(TradeTransaction).where(
            (TradeTransaction.buyer_id == user_id)
            | (TradeTransaction.seller_id == user_id)
            | (TradeTransaction.lc_issuer_id == user_id)
        )
    ).all()

    # Create CSV
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "ID",
            "Buyer ID",
            "Seller ID",
            "Amount",
            "Currency",
            "Description",
            "Status",
            "Risk Score",
            "Risk Level",
            "Created At",
        ],
    )

    writer.writeheader()
    for tx in transactions:
        writer.writerow(
            {
                "ID": tx.id,
                "Buyer ID": tx.buyer_id,
                "Seller ID": tx.seller_id,
                "Amount": f"{tx.amount:.2f}",
                "Currency": tx.currency,
                "Description": tx.description,
                "Status": tx.status.value,
                "Risk Score": f"{tx.risk_score:.1f}",
                "Risk Level": get_risk_level(tx.risk_score),
                "Created At": tx.created_at.isoformat(),
            }
        )

    return {
        "filename": f"transactions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
        "content": output.getvalue(),
        "record_count": len(transactions),
    }


@router.get("/export/documents/pdf")
def export_documents_pdf(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Export user's documents as PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF export requires reportlab. Install with: pip install reportlab"
        )
    
    user_id = current_user["user_id"]
    
    documents = session.exec(
        select(Document)
        .where(Document.owner_id == user_id)
        .order_by(Document.created_at.desc())
    ).all()
    
    # Create PDF
    from io import BytesIO
    buffer = BytesIO()
    
    filename = f"documents_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    # Title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),
        spaceAfter=30,
    )
    story.append(Paragraph("Documents Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Table data
    data = [["ID", "Doc Number", "Type", "Status", "Created At"]]
    for d in documents:
        data.append([
            str(d.id),
            d.doc_number,
            d.doc_type.value,
            d.status.value,
            d.created_at.strftime("%Y-%m-%d %H:%M"),
        ])
    
    # Create table
    table = Table(data, colWidths=[0.7*inch, 1.2*inch, 0.8*inch, 1.2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    
    story.append(table)
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return {
        "filename": filename,
        "content": pdf_content.hex(),  # Return as hex for JSON serialization
        "record_count": len(documents),
        "encoding": "base64",
    }


@router.get("/export/transactions/pdf")
def export_transactions_pdf(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Export user's transactions as PDF"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF export requires reportlab. Install with: pip install reportlab"
        )
    
    user_id = current_user["user_id"]
    
    transactions = session.exec(
        select(TradeTransaction).where(
            (TradeTransaction.buyer_id == user_id)
            | (TradeTransaction.seller_id == user_id)
            | (TradeTransaction.lc_issuer_id == user_id)
        )
    ).all()
    
    # Create PDF
    from io import BytesIO
    buffer = BytesIO()
    
    filename = f"transactions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    # Title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),
        spaceAfter=30,
    )
    story.append(Paragraph("Transactions Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Table data
    data = [["ID", "Buyer", "Seller", "Amount", "Status", "Risk", "Created"]]
    for tx in transactions:
        data.append([
            str(tx.id),
            str(tx.buyer_id),
            str(tx.seller_id),
            f"{tx.amount:.2f}",
            tx.status.value,
            f"{tx.risk_score:.1f}",
            tx.created_at.strftime("%Y-%m-%d"),
        ])
    
    # Create table
    table = Table(data, colWidths=[0.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.6*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(table)
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return {
        "filename": filename,
        "content": pdf_content.hex(),  # Return as hex for JSON serialization
        "record_count": len(transactions),
        "encoding": "base64",
    }


# -------------------------
# ACTIVITY/AUDIT LOG
# -------------------------
@router.get("/ledger/activity")
def get_activity_log(
    days: int = 30,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get activity log (ledger entries) for user's documents over past N days"""
    user_id = current_user["user_id"]

    # Get user's documents
    user_docs = session.exec(
        select(Document.id).where(Document.owner_id == user_id)
    ).all()

    if not user_docs:
        return {
            "user_id": user_id,
            "period_days": days,
            "total_activities": 0,
            "activities": [],
        }

    # Get ledger entries from past N days
    start_date = datetime.utcnow() - timedelta(days=days)
    activities = session.exec(
        select(LedgerEntry)
        .where(
            (LedgerEntry.document_id.in_(user_docs))
            & (LedgerEntry.timestamp >= start_date)
        )
        .order_by(LedgerEntry.timestamp.desc())
    ).all()

    return {
        "user_id": user_id,
        "period_days": days,
        "total_activities": len(activities),
        "activities": [
            {
                "id": a.id,
                "document_id": a.document_id,
                "action": a.action,
                "actor_id": a.actor_id,
                "timestamp": a.timestamp.isoformat(),
                "meta": a.meta,
            }
            for a in activities
        ],
    }


# -------------------------
# KPI DASHBOARD
# -------------------------
@router.get("/dashboard/kpis")
def get_dashboard_kpis(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get comprehensive KPI dashboard for user"""
    user_id = current_user["user_id"]

    # Documents KPI
    total_docs = session.exec(
        select(func.count(Document.id)).where(Document.owner_id == user_id)
    ).one()

    verified_docs = session.exec(
        select(func.count(Document.id)).where(
            (Document.owner_id == user_id) & (Document.status == DocumentStatus.VERIFIED)
        )
    ).one()

    # Transactions KPI
    transactions = session.exec(
        select(TradeTransaction).where(
            (TradeTransaction.buyer_id == user_id)
            | (TradeTransaction.seller_id == user_id)
            | (TradeTransaction.lc_issuer_id == user_id)
        )
    ).all()

    settled_tx = sum(1 for t in transactions if t.status == TransactionStatus.COMPLETED)
    total_volume = sum(t.amount for t in transactions) if transactions else 0

    # Risk KPI
    avg_risk = (
        sum(t.risk_score for t in transactions) / len(transactions)
        if transactions
        else 0
    )
    critical_risk = sum(1 for t in transactions if t.risk_score >= 60)

    # Activity KPI
    recent_activity = session.exec(
        select(func.count(LedgerEntry.id)).where(
            LedgerEntry.timestamp >= datetime.utcnow() - timedelta(days=7)
        )
    ).one()

    return {
        "document_kpis": {
            "total": total_docs,
            "verified": verified_docs,
            "verification_rate": round(
                (verified_docs / total_docs * 100) if total_docs > 0 else 0, 1
            ),
        },
        "transaction_kpis": {
            "total": len(transactions),
            "settled": settled_tx,
            "settlement_rate": round(
                (settled_tx / len(transactions) * 100) if transactions else 0, 1
            ),
            "total_volume": round(total_volume, 2),
        },
        "risk_kpis": {
            "average_score": round(avg_risk, 1),
            "critical_count": critical_risk,
            "health_score": round(max(0, 100 - avg_risk), 1),
        },
        "activity_kpis": {"articles_7days": recent_activity},
    }

# -------------------------
# ORG-LEVEL DASHBOARD
# -------------------------
@router.get("/org/dashboard/summary")
def get_org_dashboard_summary(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get comprehensive org-level dashboard summary"""
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    # Get current user for org_name
    current_user_obj = session.get(User, user_id)
    if not current_user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Org-level queries (all users in same org or admin sees all)
    if role == "admin":
        transactions = session.exec(select(TradeTransaction)).all()
        users = session.exec(select(User)).all()
    else:
        transactions = session.exec(
            select(TradeTransaction).join(
                User,
                (TradeTransaction.buyer_id == User.id) |
                (TradeTransaction.seller_id == User.id) |
                (TradeTransaction.lc_issuer_id == User.id)
            ).where(User.org_name == current_user_obj.org_name)
        ).all()
        users = session.exec(
            select(User).where(User.org_name == current_user_obj.org_name)
        ).all()
    
    # ============ TRANSACTION METRICS ============
    total_amount = sum(t.amount for t in transactions) if transactions else 0
    
    # Total bought (user as buyer)
    total_bought = sum(
        t.amount for t in transactions if t.buyer_id == user_id
    ) if transactions else 0
    
    # Total sold (user as seller)
    total_sold = sum(
        t.amount for t in transactions if t.seller_id == user_id
    ) if transactions else 0
    
    # Status breakdown
    status_breakdown = {}
    for status in TransactionStatus:
        count = sum(1 for t in transactions if t.status == status)
        status_breakdown[status.value] = count
    
    # ============ RISK METRICS ============
    org_risk_score = 0.0
    if transactions:
        org_risk_score = sum(t.risk_score for t in transactions) / len(transactions)
    
    # ============ TIME METRICS ============
    avg_completion_time = 0.0
    if transactions:
        completed = [t for t in transactions if t.status == TransactionStatus.COMPLETED]
        if completed:
            completion_times = [
                (t.updated_at - t.created_at).days for t in completed
            ]
            avg_completion_time = sum(completion_times) / len(completion_times)
    
    # ============ TOP 3 RISKY USERS ============
    risky_users = sorted(
        users,
        key=lambda u: (u.disputed_transactions / max(1, u.completed_transactions + u.disputed_transactions)) * 100,
        reverse=True
    )[:3]
    
    # ============ TOP 3 HIGH TRANSACTION USERS ============
    user_totals = []
    for u in users:
        bought = sum(t.amount for t in transactions if t.buyer_id == u.id) if transactions else 0
        sold = sum(t.amount for t in transactions if t.seller_id == u.id) if transactions else 0
        total = bought + sold
        if total > 0:
            user_totals.append({
                "user_id": u.id,
                "name": u.name,
                "email": u.email,
                "total_amount": total,
                "total_bought": bought,
                "total_sold": sold,
            })
    
    high_volume_users = sorted(
        user_totals,
        key=lambda x: x["total_amount"],
        reverse=True
    )[:3]
    
    # ============ CORRUPTED DOCUMENTS ============
    corrupted_docs = []
    user_docs = session.exec(
        select(Document).where(Document.owner_id == user_id)
    ).all()
    
    for doc in user_docs:
        try:
            filepath = os.path.join("uploaded_files", doc.file_url)
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    content = f.read()
                computed_hash = hashlib.sha256(content).hexdigest()
                if computed_hash != doc.hash:
                    corrupted_docs.append({
                        "doc_id": doc.id,
                        "doc_number": doc.doc_number,
                        "doc_type": doc.doc_type.value,
                        "status": "CORRUPTED",
                    })
        except Exception:
            corrupted_docs.append({
                "doc_id": doc.id,
                "doc_number": doc.doc_number,
                "doc_type": doc.doc_type.value,
                "status": "FILE_MISSING",
            })
    
    return {
        "org_name": current_user_obj.org_name,
        "summary": {
            "total_transaction_amount": round(total_amount, 2),
            "total_bought": round(total_bought, 2),
            "total_sold": round(total_sold, 2),
        },
        "status_breakdown": status_breakdown,
        "risk_metrics": {
            "org_risk_score": round(org_risk_score, 2),
            "avg_completion_days": round(avg_completion_time, 1),
        },
        "top_3_risky_users": [
            {
                "user_id": u.id,
                "name": u.name,
                "email": u.email,
                "risk_score": round((u.disputed_transactions / max(1, u.completed_transactions + u.disputed_transactions)) * 100, 2),
                "completed": u.completed_transactions,
                "disputed": u.disputed_transactions,
            }
            for u in risky_users
        ],
        "top_3_high_volume_users": high_volume_users,
        "corrupted_documents": corrupted_docs,
        "total_users": len(users),
        "total_transactions": len(transactions),
    }


@router.get("/org/dashboard/timeline")
def get_org_transaction_timeline(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get transaction timeline (completed/disputed count by day) for org"""
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    # Get current user for org_name
    current_user_obj = session.get(User, user_id)
    if not current_user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get org transactions
    if role == "admin":
        transactions = session.exec(select(TradeTransaction)).all()
    else:
        transactions = session.exec(
            select(TradeTransaction).join(
                User,
                (TradeTransaction.buyer_id == User.id) |
                (TradeTransaction.seller_id == User.id) |
                (TradeTransaction.lc_issuer_id == User.id)
            ).where(User.org_name == current_user_obj.org_name)
        ).all()
    
    # Group by created_at date
    timeline = {}
    for tx in transactions:
        date_key = tx.created_at.strftime("%Y-%m-%d")
        if date_key not in timeline:
            timeline[date_key] = {"completed": 0, "disputed": 0}
        
        if tx.status == TransactionStatus.COMPLETED:
            timeline[date_key]["completed"] += 1
        elif tx.status == TransactionStatus.DISPUTED:
            timeline[date_key]["disputed"] += 1
    
    # Sort by date
    sorted_timeline = dict(sorted(timeline.items()))
    
    return {
        "org_name": current_user_obj.org_name,
        "timeline": sorted_timeline,
    }