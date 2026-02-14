import os
import jwt
import hashlib

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Response,
    Cookie,
    UploadFile,
    File,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from sqlmodel import SQLModel, Session, select
from sqlalchemy import asc

from app.database import engine, get_session
from app.models import User, Document, LedgerEntry, Transaction
from app.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    get_current_user,
    require_role,
)

from jwt import ExpiredSignatureError, InvalidTokenError


# ---------------- CONFIG ----------------

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

app = FastAPI()

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DB INIT ----------------

SQLModel.metadata.create_all(engine)

# WEEK 1 – AUTH

@app.post("/create-user")
def create_user(
    name: str,
    email: str,
    password: str,
    role: str,
    org_name: str,
    session: Session = Depends(get_session),
):
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role,
        org_name=org_name,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": "User created"}


@app.post("/login")
def login(
    email: str,
    password: str,
    response: Response,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email)).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        {
            "user_id": user.id,
            "role": user.role,
            "org": user.org_name,
        }
    )

    refresh_token = create_refresh_token({"user_id": user.id})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
    )

    return {"access_token": access_token}


@app.post("/refresh")
def refresh(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(
        {"user_id": payload["user_id"]}
    )

    return {"access_token": new_access_token}



# WEEK 2 – PROTECTED ROUTES


@app.get("/protected")
def protected(user: dict = Depends(get_current_user)):
    return {"message": "Protected route", "user": user}


@app.get("/admin-only")
def admin_only(user=Depends(require_role("admin"))):
    return {"message": "Admin access granted"}


@app.get("/user")
def get_user_profile(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = session.get(User, current_user["user_id"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "name": user.name,
        "email": user.email,
        "org": user.org_name,
        "role": user.role,
    }



# WEEK 3 – DOCUMENTS & LEDGER


def calculate_file_hash(file_bytes: bytes) -> str:
    sha = hashlib.sha256()
    sha.update(file_bytes)
    return sha.hexdigest()


@app.post("/upload")
def upload_document(
    doc_number: str,
    seller_id: int,
    doc_type: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):

    os.makedirs("files", exist_ok=True)

    file_bytes = file.file.read()
    file_hash = calculate_file_hash(file_bytes)

    file_path = f"files/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    allowed_types = ["PO", "BOL", "LOC", "INVOICE"]

    if doc_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid document type")


    document = Document(
        doc_type=doc_type,
        doc_number=doc_number,
        file_url=file.filename,
        file_hash=file_hash,
        owner_id=current_user["user_id"],
        buyer_id=current_user["user_id"],
        seller_id=seller_id,
        status="CREATED",
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=current_user["user_id"],
        action="CREATED",
        extra_data={"seller_id": seller_id},
    )

    session.add(ledger)
    session.commit()

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "file_name": document.file_url,
        "file_hash": file_hash,
    }



# @app.get("/documents")
# def get_documents(
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session),
# ):
#     user_id = current_user["user_id"]
#     role = current_user["role"]

#     if role == "buyer":
#         docs = session.exec(
#             select(Document).where(Document.buyer_id == user_id)
#         ).all()
#     elif role == "seller":
#         docs = session.exec(
#             select(Document).where(Document.seller_id == user_id)
#         ).all()
#     else:
#         docs = session.exec(select(Document)).all()

#     return [
#         {
#             "id": d.id,
#             "doc_number": d.doc_number,
#             "status": d.status,
#             "doc_type": d.doc_type,
#         }
#         for d in docs
#     ]

@app.get("/documents")
def get_documents(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    role = current_user["role"]
    user_id = current_user["user_id"]

    if role in ["bank", "auditor"]:
        docs = session.exec(select(Document)).all()
    else:
        docs = session.exec(
            select(Document).where(
                (Document.buyer_id == user_id) |
                (Document.seller_id == user_id)
            )
        ).all()

    return [
        {
            "id": d.id,
            "doc_number": d.doc_number,
            "status": d.status,
            "doc_type": d.doc_type,
        }
        for d in docs
    ]




# @app.get("/document")
# def get_document(
#     id: int,
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session),
# ):
#     document = session.get(Document, id)

#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found")

#     if (
#         document.buyer_id != current_user["user_id"]
#         and document.seller_id != current_user["user_id"]
#         and current_user["role"] not in ["bank", "auditor"]
#     ):
#         raise HTTPException(status_code=403, detail="Access denied")

#     ledger_entries = session.exec(
#         select(LedgerEntry)
#         .where(LedgerEntry.document_id == id)
#         .order_by(asc(LedgerEntry.created_at))
#     ).all()

#     # return {
#     #     "document": {
#     #         "id": document.id,
#     #         "doc_number": document.doc_number,
#     #         "doc_type": document.doc_type,
#     #         "status": document.status,
#     #         "file_url": document.file_url,
#     #     },
#         # "ledger": [
#         #     {
#         #         "action": l.action,
#         #         "actor_id": l.actor_id,
#         #         "extra_data": l.extra_data,
#         #         "created_at": l.created_at,
#         #     }
#         #     for l in ledger_entries
#         # ],
        
#     ledger_data = []

#     for l in ledger_entries:
#         actor = session.get(User, l.actor_id)

#         ledger_data.append({
#                 "action": l.action,
#                 "actor_name": actor.name if actor else "Unknown",
#                 "actor_role": actor.role if actor else "Unknown",
#                 "actor_org": actor.org_name if actor else "Unknown",
#                 "created_at": l.created_at,
#             })

#     return {
#             "document": 
#             {
#                 "id": document.id,
#                 "doc_number": document.doc_number,
#                 "doc_type": document.doc_type,
#                 "status": document.status,
#                 "file_url": document.file_url,
#             },
#             "ledger": ledger_data,
#         }



@app.get("/document")
def get_document(
    id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    document = session.get(Document, id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if (
        document.buyer_id != current_user["user_id"]
        and document.seller_id != current_user["user_id"]
        and current_user["role"] not in ["bank", "auditor"]
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    ledger_entries = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.document_id == id)
        .order_by(asc(LedgerEntry.created_at))
    ).all()

    return {
        "document": {
            "id": document.id,
            "doc_number": document.doc_number,
            "status": document.status,
            "file_url": document.file_url,
            "is_compromised": document.is_compromised,
            "doc_type": document.doc_type,
        },
        "ledger": [
            {
                "action": l.action,
                "actor_id": l.actor_id,
                "actor_name": session.get(User, l.actor_id).name,
                "actor_role": session.get(User, l.actor_id).role,
                "actor_org": session.get(User, l.actor_id).org_name,
                "extra_data": l.extra_data,
                "created_at": l.created_at,
            }
            for l in ledger_entries
        ],
    }




@app.get("/file")
def get_file(file_url: str):
    path = f"files/{file_url}"

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=path, filename=file_url)



@app.post("/action")
def perform_action(
    doc_id: int,
    action: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    document = session.get(Document, doc_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    role = current_user["role"]

    role_action_map = {
        "SHIP": "seller",
        "RECEIVE": "buyer",
        "ISSUE_LOC": "bank",
        "PAY": "bank",
        "VERIFY": "auditor",
    }

    if action in role_action_map and role != role_action_map[action]:
        raise HTTPException(status_code=403, detail="Action not allowed")

    document.status = action
    session.add(document)

    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=current_user["user_id"],
        action=action,
        extra_data={},
    )

    session.add(ledger)
    session.commit()

    return {
        "message": "Action completed",
        "doc_id": document.id,
        "new_status": action,
    }

# week 4
@app.get("/verify-hash")
def verify_document_hash(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session =Depends(get_session),
):
    document = session.get(Document, document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not Found")
    
    file_path = f"files/{document.file_url}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing from storage")
    
    # Read file again
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    recalculated_hash =  calculate_file_hash(file_bytes)

    is_valid = recalculated_hash == document.file_hash

    return {
        "document_id": document.id,
        "stored_hash": document.file_hash,
        "recalculated_hash": recalculated_hash,
        "is_valid": is_valid,
    }


# week-5
@app.post("/po/create")
def create_po_with_transaction(seller_id: int,
                               currency: str,
                               amount: float,
                               file: UploadFile = File(...),
                               current_user: dict =Depends(get_current_user),
                               session: Session = Depends(get_session),
                               ):
    # only buyer can create Po
    if current_user["role"] != "buyer":
        raise HTTPException(status_code=403,detail="Only Buyers can create PO")
    
    os.makedirs("files", exist_ok=True)

    file_bytes = file.file.read()
    file_hash = calculate_file_hash(file_bytes)

    file_path = f"files/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # create transaction
    tx = Transaction(buyer_id=current_user["user_id"],
                     seller_id=seller_id,
                     currency=currency,
                     amount=amount,
                     status="pending",)
    session.add(tx)
    session.commit()
    session.refresh(tx)

    # create PO document
    document = Document(doc_type="PO",
                        doc_number=file.filename,
                        file_url=file.filename,
                        file_hash=file_hash,
                        owner_id=current_user["user_id"],
                        buyer_id=current_user["user_id"],
                        seller_id=seller_id,
                        status="ISSUED",)
    session.add(document)
    session.commit()
    session.refresh(document)

    # create ledger entry
    ledger = LedgerEntry(document_id=document.id,
                         actor_id=current_user["user_id"],
                         action="ISSUED",
                         extra_data={"transaction_id": tx.id},)
    session.add(ledger)
    session.commit()

    return {
        "message": "PO created with transaction",
        "transaction_id": tx.id,
        "document_id": document.id,
        "status": tx.status,
    }
    

@app.post("/loc/issue")
def issue_loc_for_po(po_id: int,
                     file: UploadFile = File(...),
                     current_user: dict = Depends(get_current_user),
                     session: Session = Depends(get_session),):
    
    # only bank can issue LOC
    if current_user["role"] != "bank":
        raise HTTPException(status_code=403, detail="only bank can issue LOC")
    
    po_doc = session.get(Document, po_id)
    if not po_doc or po_doc.doc_type != "PO":
        raise HTTPException(status_code=400, detail="Invalid PO")
    
    # to find transaction id from ledger entry
    po_ledger = session.exec(select(LedgerEntry)
                             .where(LedgerEntry.document_id == po_id)
                             .order_by(LedgerEntry.created_at.desc())).first()
    
    if not po_ledger or "transaction_id" not in po_ledger.extra_data:
        raise HTTPException(status_code=400, detail="PO is not linked to a transaction")
    
    tx_id = po_ledger.extra_data["transaction_id"]

    # save LOC file
    os.makedirs("files", exist_ok=True)
    file_bytes = file.file.read()
    file_hash = calculate_file_hash(file_bytes)
    
    file_path = f"files/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # create LOC document
    loc_doc = Document(doc_type="LOC",
                       doc_number=file.filename,
                       file_url=file.filename,
                       file_hash=file_hash,
                       owner_id=current_user["user_id"],
                       buyer_id=po_doc.buyer_id,
                       seller_id=po_doc.seller_id,
                       status="ISSUED",
                       )
    session.add(loc_doc)
    session.commit()
    session.refresh(loc_doc)

    # create ledger entry linked to transaction + PO
    ledger = LedgerEntry(document_id=loc_doc.id,
                         actor_id=current_user["user_id"],
                         action="ISSUED",
                         extra_data={"transaction_id": tx_id, "po_id": po_id},             
                        )

    session.add(ledger)
    session.commit()

    return {
        "message": "LOC issued successfully",
        "loc_id": loc_doc.id,
        "transaction_id": tx_id,
        "po_id": po_id,
    }


@app.post("/audit/verify")
def verify_po_and_loc(po_id: int,
                      current_user: dict =Depends(get_current_user),
                      session: Session = Depends(get_session),):
    # only auditor can verify
    if current_user["role"] != "auditor":
        raise HTTPException(status_code=403, detail="Only auditor can verify")
    
    po_doc = session.get(Document, po_id)
    if not po_doc or po_doc.doc_type != "PO":
        raise HTTPException(status_code=400, detail="Invalid PO")
    
    # find transaction_id from Po ledger
    po_ledger = session.exec(select(LedgerEntry)
                             .where(LedgerEntry.document_id == po_id)
                             .order_by(LedgerEntry.created_at.desc())).first()
    
    if not po_ledger or "transaction_id" not in po_ledger.extra_data:
        raise HTTPException(status_code=400, detail="PO is not linked to a transaction")
    
    tx_id = po_ledger.extra_data["transaction_id"]

    # find LOC linked to same transaction
    loc_leder = session.exec(select(LedgerEntry)
                             .where(LedgerEntry.extra_data["transaction_id"].as_integer() == tx_id,)).all()
    
    loc_ids = [l.document_id 
               for l in loc_leder
               if session.get(Document, l.document_id).doc_type == "LOC"]
    
    if not loc_ids:
        raise HTTPException(status_code=400, detail="No LOC found for this transaction")
    
    loc_id = loc_ids[0]

    # create ledger entry for PO
    ledger_po = LedgerEntry(document_id=po_id,
                            actor_id=current_user["user_id"],
                            action="VERIFIED",
                            extra_data={"transaction_id": tx_id},
                            )
    
    # create ledger entry for LOC
    ledger_loc = LedgerEntry(document_id=loc_id,
                            actor_id=current_user["user_id"],
                            action="VERIFIED",
                            extra_data={"transaction_id": tx_id},
                            )
    
    session.add(ledger_po)
    session.add(ledger_loc)

    # update transaction status
    tx = session.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    
    tx.status = "in_progress"
    session.add(tx)
    session.commit()

    return {
        "message": "Po and LOC verified",
        "transaction_id": tx_id,
        "new_status": tx.status,
    }



@app.post("/bol/upload")
def upload_bol_for_tranaction(transaction_id: int,
                              tracking_id: str,
                              file: UploadFile = File(...),
                              current_user: dict = Depends(get_current_user),
                              session: Session = Depends(get_session),
                              ):
    # only seller can upload BOL
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only Seller can upload BOL")
    
    tx = session.get(Transaction, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # only if transaction is in_progress
    if tx.status != "in_progress":
        raise HTTPException(status_code=400, detail="Transaction not in progress")
    
    os.makedirs("files", exist_ok=True)
    file_bytes = file.file.read()
    file_hash = calculate_file_hash(file_bytes)

    file_path = f"files/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # create BOL document
    bol_doc = Document(doc_type="BOL",
                       doc_number=file.filename,
                       file_url=file.filename,
                       file_hash=file_hash,
                       owner_id=current_user["user_id"],
                       buyer_id=tx.buyer_id,
                       seller_id=current_user["user_id"],
                       status="SHIPPED",
                        )
    
    session.add(bol_doc)
    session.commit()
    session.refresh(bol_doc)

    # create ledger entry 
    ledger = LedgerEntry(document_id=bol_doc.id,
                         actor_id=current_user["user_id"],
                         action="SHIPPED",
                         extra_data={"transaction_id": transaction_id,"tracking_id": tracking_id,},
                        )
    
    session.add(ledger)
    session.commit()

    return {
        "message": "BOL uploaded and shipment recorded",
        "bol_id": bol_doc.id,
        "transaction_id": transaction_id,
    }



@app.post("/invoice/issue")
def issue_invoice_for_transaction(transaction_id: int,
                                    file: UploadFile = File(...),
                                    current_user: dict = Depends(get_current_user),
                                    session: Session = Depends(get_session),
                                ):
    #  Only seller can issue INVOICE
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only seller can issue invoice")

    tx = session.get(Transaction, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Only if transaction is in_progress
    if tx.status != "in_progress":
        raise HTTPException(status_code=400, detail="Transaction not in progress")

    os.makedirs("files", exist_ok=True)
    file_bytes = file.file.read()
    file_hash = calculate_file_hash(file_bytes)

    file_path = f"files/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Create INVOICE document
    invoice_doc = Document(doc_type="INVOICE",
                            doc_number=file.filename,
                            file_url=file.filename,
                            file_hash=file_hash,
                            owner_id=current_user["user_id"],
                            buyer_id=tx.buyer_id,
                            seller_id=current_user["user_id"],
                            status="ISSUED",
                            )

    session.add(invoice_doc)
    session.commit()
    session.refresh(invoice_doc)

    # Create ledger entry linked to transaction
    ledger = LedgerEntry(
        document_id=invoice_doc.id,
        actor_id=current_user["user_id"],
        action="ISSUED",
        extra_data={"transaction_id": transaction_id},
    )

    session.add(ledger)
    session.commit()

    return {
        "message": "Invoice issued successfully",
        "invoice_id": invoice_doc.id,
        "transaction_id": transaction_id,
    }


@app.post("/bol/receive")
def receive_bol_for_transaction(
    bol_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Only buyer can mark BOL as received
    if current_user["role"] != "buyer":
        raise HTTPException(status_code=403, detail="Only buyer can receive goods")

    bol_doc = session.get(Document, bol_id)
    if not bol_doc or bol_doc.doc_type != "BOL":
        raise HTTPException(status_code=400, detail="Invalid BOL")

    # Get transaction_id from BOL ledger
    bol_ledger = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.document_id == bol_id)
        .order_by(LedgerEntry.created_at.desc())
    ).first()

    if not bol_ledger or "transaction_id" not in bol_ledger.extra_data:
        raise HTTPException(status_code=400, detail="BOL not linked to transaction")

    tx_id = bol_ledger.extra_data["transaction_id"]

    tx = session.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Only if transaction is in_progress
    if tx.status != "in_progress":
        raise HTTPException(status_code=400, detail="Transaction not in progress")

    #  Create ledger entry for RECEIVED
    ledger = LedgerEntry(
        document_id=bol_id,
        actor_id=current_user["user_id"],
        action="RECEIVED",
        extra_data={"transaction_id": tx_id},
    )

    session.add(ledger)
    session.commit()

    return {
        "message": "Goods received and recorded",
        "bol_id": bol_id,
        "transaction_id": tx_id,
    }


@app.post("/invoice/pay")
def pay_invoice_for_transaction(
    invoice_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Only bank can pay
    if current_user["role"] != "bank":
        raise HTTPException(status_code=403, detail="Only bank can pay invoice")

    invoice_doc = session.get(Document, invoice_id)
    if not invoice_doc or invoice_doc.doc_type != "INVOICE":
        raise HTTPException(status_code=400, detail="Invalid INVOICE")

    # Get transaction_id from INVOICE ledger
    invoice_ledger = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.document_id == invoice_id)
        .order_by(LedgerEntry.created_at.desc())
    ).first()

    if not invoice_ledger or "transaction_id" not in invoice_ledger.extra_data:
        raise HTTPException(status_code=400, detail="Invoice not linked to transaction")

    tx_id = invoice_ledger.extra_data["transaction_id"]

    tx = session.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Only if transaction is in_progress
    if tx.status != "in_progress":
        raise HTTPException(status_code=400, detail="Transaction not in progress")

    #  Create ledger entry for PAID
    ledger = LedgerEntry(
        document_id=invoice_id,
        actor_id=current_user["user_id"],
        action="PAID",
        extra_data={"transaction_id": tx_id},
    )

    session.add(ledger)

    #  Update transaction status to completed
    tx.status = "completed"
    session.add(tx)
    session.commit()

    return {
        "message": "Invoice paid and transaction completed",
        "invoice_id": invoice_id,
        "transaction_id": tx_id,
        "new_status": tx.status,
    }


@app.get("/transactions")
def list_transactions(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    role = current_user["role"]
    user_id = current_user["user_id"]

    # Buyer sees transactions where they are buyer
    if role == "buyer":
        txs = session.exec(select(Transaction).where(Transaction.buyer_id == user_id)).all()
    # Seller sees transactions where they are seller
    elif role == "seller":
        txs = session.exec(select(Transaction).where(Transaction.seller_id == user_id)).all()
    # Bank/Auditor/Admin see all (or restrict later)
    else:
        txs = session.exec(select(Transaction)).all()

    return [
        {
            "id": tx.id,
            "buyer_id": tx.buyer_id,
            "seller_id": tx.seller_id,
            "currency": tx.currency,
            "amount": tx.amount,
            "status": tx.status,
            "created_at": tx.created_at,
        }
        for tx in txs
    ]



# @app.get("/transaction")
# def get_transaction_detail(
#     id: int,
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session),
# ):
#     tx = session.get(Transaction, id)
#     if not tx:
#         raise HTTPException(status_code=404, detail="Transaction not found")

#     role = current_user["role"]
#     user_id = current_user["user_id"]

#     # Access control
#     if role == "buyer" and tx.buyer_id != user_id:
#         raise HTTPException(status_code=403, detail="Access denied")
#     if role == "seller" and tx.seller_id != user_id:
#         raise HTTPException(status_code=403, detail="Access denied")

#     # Find all ledger entries linked to this transaction
#     ledgers = session.exec(
#         select(LedgerEntry)
#         .where(LedgerEntry.extra_data["transaction_id"].as_integer() == id)
#         .order_by(asc(LedgerEntry.created_at))
#     ).all()

#     # Get all document IDs involved in this transaction
#     doc_ids = list({l.document_id for l in ledgers})

#     documents = [session.get(Document, doc_id) for doc_id in doc_ids]

#     return {
#         "transaction": {
#             "id": tx.id,
#             "buyer_id": tx.buyer_id,
#             "seller_id": tx.seller_id,
#             "currency": tx.currency,
#             "amount": tx.amount,
#             "status": tx.status,
#             "created_at": tx.created_at,
#         },
#         "documents": [
#             {
#                 "id": d.id,
#                 "doc_type": d.doc_type,
#                 "status": d.status,
#                 "file_url": d.file_url,
#             }
#             for d in documents if d
#         ],
#         "ledger": [
#             {
#                 "document_id": l.document_id,
#                 "action": l.action,
#                 "actor_id": l.actor_id,
#                 "created_at": l.created_at,
#                 "extra_data": l.extra_data,
#             }
#             for l in ledgers
#         ],
#     }





@app.get("/transaction")
def get_transaction_detail(
    id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    tx = session.get(Transaction, id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    role = current_user["role"]
    user_id = current_user["user_id"]

    if role == "buyer" and tx.buyer_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if role == "seller" and tx.seller_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    ledgers = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.extra_data["transaction_id"].as_integer() == id)
        .order_by(asc(LedgerEntry.created_at))
    ).all()

    doc_ids = list({l.document_id for l in ledgers})
    documents = [session.get(Document, doc_id) for doc_id in doc_ids]

    return {
        "transaction": {
            "id": tx.id,
            "buyer_id": tx.buyer_id,
            "seller_id": tx.seller_id,
            "currency": tx.currency,
            "amount": tx.amount,
            "status": tx.status,
            "created_at": tx.created_at,
        },
        "documents": [
            {
                "id": d.id,
                "doc_type": d.doc_type,
                "status": d.status,
                "file_url": d.file_url,
            }
            for d in documents if d
        ],
        "ledger": [
            {
                "document_id": l.document_id,
                "action": l.action,
                "actor_id": l.actor_id,
                "actor_role": session.get(User, l.actor_id).role,
                "created_at": l.created_at,
                "extra_data": l.extra_data,
            }
            for l in ledgers
        ],
    }



# week:6
@app.get("/alerts/compromised-documents")
def list_compromised_documents(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Only admin or auditor can see all compromised docs
    if current_user["role"] not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    docs = session.exec(select(Document).where(Document.is_compromised == True)).all()

    return [
        {
            "id": d.id,
            "doc_type": d.doc_type,
            "doc_number": d.doc_number,
            "file_url": d.file_url,
            "owner_id": d.owner_id,
            "status": d.status,
            "is_compromised": d.is_compromised,
        }
        for d in docs
    ]



@app.get("/alerts/audit-logs")
def list_audit_logs(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user["role"] not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    logs = session.exec(
        select(AuditLog).order_by(AuditLog.timestamp.desc())
    ).all()

    return [
        {
            "id": log.id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


from app.tasks import integrity_check_job

@app.post("/admin/run-integrity-check")
def run_integrity_check_now(
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can trigger check")

    integrity_check_job.delay()
    return {"message": "Integrity check triggered"}

