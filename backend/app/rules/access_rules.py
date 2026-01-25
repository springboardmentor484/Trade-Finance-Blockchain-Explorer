from typing import List
from app.models import DocumentStatus, UserRole


def get_allowed_actions(
    role: UserRole,
    current_status: DocumentStatus,
) -> List[DocumentStatus]:
    """
    Returns allowed next actions based on role + current document status
    """

    rules = {
        UserRole.BUYER: {
            DocumentStatus.ISSUED: [DocumentStatus.ACCEPTED],
        },
        UserRole.SELLER: {
            DocumentStatus.ACCEPTED: [DocumentStatus.SHIPPED],
        },
        UserRole.BANK: {
            DocumentStatus.RECEIVED: [DocumentStatus.VERIFIED],
        },
        UserRole.AUDITOR: {},
    }

    return rules.get(role, {}).get(current_status, [])
