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
from app.models import User, Document, LedgerEntry
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

    # return {
    #     "document": {
    #         "id": document.id,
    #         "doc_number": document.doc_number,
    #         "doc_type": document.doc_type,
    #         "status": document.status,
    #         "file_url": document.file_url,
    #     },
        # "ledger": [
        #     {
        #         "action": l.action,
        #         "actor_id": l.actor_id,
        #         "extra_data": l.extra_data,
        #         "created_at": l.created_at,
        #     }
        #     for l in ledger_entries
        # ],
        
    ledger_data = []

    for l in ledger_entries:
        actor = session.get(User, l.actor_id)

        ledger_data.append({
                "action": l.action,
                "actor_name": actor.name if actor else "Unknown",
                "actor_role": actor.role if actor else "Unknown",
                "actor_org": actor.org_name if actor else "Unknown",
                "created_at": l.created_at,
            })

    return {
            "document": 
            {
                "id": document.id,
                "doc_number": document.doc_number,
                "doc_type": document.doc_type,
                "status": document.status,
                "file_url": document.file_url,
            },
            "ledger": ledger_data,
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