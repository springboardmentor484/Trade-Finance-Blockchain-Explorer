from app.models import DocumentStatus, UserRole

# -------------------------------------------------
# ROLE → ALLOWED STATUS TRANSITIONS (STATE MACHINE)
# -------------------------------------------------

ROLE_ALLOWED_TRANSITIONS = {
    UserRole.BUYER: {
        DocumentStatus.ISSUED: [DocumentStatus.ACCEPTED],
        DocumentStatus.ACCEPTED: [DocumentStatus.SHIPPED],
    },
    UserRole.SELLER: {
        DocumentStatus.SHIPPED: [DocumentStatus.RECEIVED],
    },
    UserRole.BANK: {
        DocumentStatus.RECEIVED: [DocumentStatus.PAID],
        DocumentStatus.PAID: [DocumentStatus.VERIFIED],
    },
}


def validate_transition(
    role: UserRole,
    current_status: DocumentStatus,
    next_status: DocumentStatus,
):
    """
    Enforces role-based document lifecycle transitions.
    Raises ValueError if transition is invalid.
    """

    role_rules = ROLE_ALLOWED_TRANSITIONS.get(role)

    if not role_rules:
        raise ValueError(f"No rules defined for role {role.value}")

    allowed_next = role_rules.get(current_status, [])

    if next_status not in allowed_next:
        raise ValueError(
            f"Invalid transition for role {role.value}: "
            f"{current_status.value} → {next_status.value}"
        )
