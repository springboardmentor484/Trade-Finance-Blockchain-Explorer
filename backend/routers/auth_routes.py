from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import select
from backend.database import get_session
from backend.models import User
from backend.utils import verify_password, create_access_token, create_refresh_token
from fastapi.responses import JSONResponse
from sqlmodel import Session
from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlmodel import Session
import shutil
import hashlib
import json
import os

from backend.database import get_session
from backend.models import Document, LedgerEntry

router = APIRouter(prefix="/auth")

# Signup
@router.post("/signup")
def signup(user: User, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user.password = create_access_token({"password": user.password})  # simple hash
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created successfully"}

# Login
@router.post("/login")
def login(credentials: dict, response: Response, session: Session = Depends(get_session)):
    email = credentials.get("email")
    password = credentials.get("password")

    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict"
    )

    return {"access_token": access_token, "token_type": "bearer"}

# Refresh token
@router.post("/refresh")
def refresh(response: Response, refresh_token: str = Depends(lambda: None)):
    from jose import jwt, JWTError
    from fastapi import Cookie

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")
    try:
        payload = jwt.decode(refresh_token, "CHANGE_THIS_SECRET_LATER", algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        new_access_token = create_access_token({"sub": email})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/upload")
def upload_document(
    doc_number: str = Form(...),
    doc_type: str = Form(...),   # PO
    seller_id: int = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    # 1. Save file
    os.makedirs("backend/files", exist_ok=True)
    file_path = f"backend/files/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Generate file hash
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    # 3. Create Document
    document = Document(
        doc_type=doc_type,
        doc_number=doc_number,
        owner_id=seller_id,  # buyer uploads PO for seller
        file_url=file.filename,
        file_hash=file_hash,
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    # 4. Create Ledger Entry
    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=seller_id,
        action="ISSUED",
        metadata=json.dumps({"seller_id": seller_id}),
    )

    session.add(ledger)
    session.commit()

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id
    }

  