from app.models import UserRole, DocumentStatus


ROLE_ALLOWED_TRANSITIONS = {
    UserRole.BUYER: {
        DocumentStatus.SHIPPED: DocumentStatus.RECEIVED,
    },
    UserRole.SELLER: {
        DocumentStatus.ISSUED: DocumentStatus.SHIPPED,
    },
    UserRole.BANK: {
        DocumentStatus.RECEIVED: DocumentStatus.PAID,
    },
    UserRole.AUDITOR: {
        DocumentStatus.PAID: DocumentStatus.VERIFIED,
    },
}


def validate_transition(role, current_status, next_status):
    role_rules = ROLE_ALLOWED_TRANSITIONS.get(role)

    if not role_rules:
        raise ValueError("Role not allowed to perform any action")

    expected_next = role_rules.get(current_status)

    if expected_next != next_status:
        raise ValueError(
            f"Invalid transition for role {role}: "
            f"{current_status} → {next_status}"
        )
