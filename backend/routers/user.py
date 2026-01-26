from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from models import User
from schemas import UserCreate, UserRead
from utils import hash_password

router = APIRouter()

@router.post("/signup", response_model=UserRead)
def signup(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password=hash_password(user.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.database import get_session
from backend.models import PurchaseOrder
from backend.utils import can_perform_action

router = APIRouter(prefix="/buyer", tags=["Buyer"])


@router.post("/po")
def upload_po(
    seller_id: int,
    description: str,
    amount: float,
    user_role: str,
    buyer_id: int,
    session: Session = Depends(get_session)
):
    if not can_perform_action(user_role, "PO", "UPLOAD"):
        raise HTTPException(status_code=403, detail="Not allowed")

    po = PurchaseOrder(
        buyer_id=buyer_id,
        seller_id=seller_id,
        description=description,
        amount=amount
    )

    session.add(po)
    session.commit()
    session.refresh(po)

    return po