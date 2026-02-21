from typing import List, Dict, Optional
from fastapi import HTTPException, status

from ..models import DocumentStatus, UserRole

# -------------------------------------------------
# GLOBAL DOCUMENT FLOW (CANNOT BE BYPASSED)
# -------------------------------------------------

ALLOWED_STATUS_FLOW = {
    DocumentStatus.ISSUED: [DocumentStatus.ACCEPTED],
    DocumentStatus.ACCEPTED: [DocumentStatus.SHIPPED],
    DocumentStatus.SHIPPED: [DocumentStatus.RECEIVED],
    DocumentStatus.RECEIVED: [DocumentStatus.PAID],
    DocumentStatus.PAID: [DocumentStatus.VERIFIED],
}

# -------------------------------------------------
# ROLE → ALLOWED ACTIONS
# -------------------------------------------------

ROLE_ALLOWED_ACTIONS = {
    UserRole.BUYER: [
        DocumentStatus.ACCEPTED,
    ],
    UserRole.SELLER: [
        DocumentStatus.SHIPPED,
    ],
    UserRole.BANK: [
        DocumentStatus.RECEIVED,
        DocumentStatus.VERIFIED,
    ],
}

# -------------------------------------------------
# TRANSITION VALIDATION
# -------------------------------------------------

def validate_transition(
    role: UserRole,
    current_status: DocumentStatus,
    next_status: DocumentStatus,
    meta: Optional[Dict] = None,
):
    """
    Enforces:
    1. Lifecycle integrity
    2. Role-based permissions
    3. Admin override constraints
    """

    # -----------------------------
    # 1️⃣ Lifecycle enforcement
    # -----------------------------
    allowed_next = ALLOWED_STATUS_FLOW.get(current_status, [])

    if next_status not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition: {current_status} → {next_status}",
        )

    # -----------------------------
    # 2️⃣ Admin override rules
    # -----------------------------
    if role == UserRole.ADMIN:
        if not meta or not meta.get("reason"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Admin action requires audit reason in meta",
            )
        return  # Admin allowed if lifecycle + audit is satisfied

    # -----------------------------
    # 3️⃣ Role-based permission
    # -----------------------------
    allowed_actions = ROLE_ALLOWED_ACTIONS.get(role, [])

    if next_status not in allowed_actions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action",
        )

# -------------------------------------------------
# ALLOWED ACTIONS RESOLVER
# -------------------------------------------------

def get_allowed_actions(
    role: UserRole,
    current_status: DocumentStatus,
) -> List[DocumentStatus]:
    """
    Returns allowed NEXT actions for UI / clients
    """

    lifecycle_next = ALLOWED_STATUS_FLOW.get(current_status, [])

    if role == UserRole.ADMIN:
        return lifecycle_next

    role_actions = ROLE_ALLOWED_ACTIONS.get(role, [])

    return [
        status
        for status in lifecycle_next
        if status in role_actions
    ]
