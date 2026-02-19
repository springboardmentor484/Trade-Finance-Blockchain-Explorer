from enum import Enum
from typing import Dict, List


# =====================================================
# ACTION ENUM (ALL SYSTEM ACTIONS)
# =====================================================

class Action(str, Enum):
    # Transactions
    CREATE_TRANSACTION = "CREATE_TRANSACTION"
    VIEW_TRANSACTION = "VIEW_TRANSACTION"
    UPDATE_STATUS = "UPDATE_STATUS"
    MARK_DISPUTED = "MARK_DISPUTED"
    UPDATE_TRANSACTION_STATUS = "UPDATE_TRANSACTION_STATUS"


    # Workflow Steps
    CREATE_PO = "CREATE_PO"
    ISSUE_LOC = "ISSUE_LOC"
    VERIFY_TRANSACTION = "VERIFY_TRANSACTION"
    COMPLETE_TRANSACTION = "COMPLETE_TRANSACTION"

    # Exports
    EXPORT_TRANSACTIONS = "EXPORT_TRANSACTIONS"
    EXPORT_LEDGER = "EXPORT_LEDGER"
    EXPORT_PDF = "EXPORT_PDF"

    # Admin
    VIEW_ALL = "VIEW_ALL"


# =====================================================
# ROLE → ACTION MATRIX
# =====================================================

ROLE_ACTION_MATRIX: Dict[str, List[Action]] = {
    "admin": list(Action),
    

    "buyer": [
        Action.CREATE_TRANSACTION,
        Action.UPDATE_TRANSACTION_STATUS,
        Action.VIEW_TRANSACTION,
        Action.MARK_DISPUTED,
        Action.CREATE_PO,
        Action.EXPORT_TRANSACTIONS,
        Action.EXPORT_PDF,
    ],

    "seller": [
        Action.VIEW_TRANSACTION,
        Action.UPDATE_TRANSACTION_STATUS,
        Action.MARK_DISPUTED,
        Action.EXPORT_TRANSACTIONS,
        Action.EXPORT_PDF,
    ],

    "bank": [
        Action.VIEW_TRANSACTION,
        Action.UPDATE_TRANSACTION_STATUS,
        Action.ISSUE_LOC,
        Action.COMPLETE_TRANSACTION,
        Action.EXPORT_TRANSACTIONS,
        Action.EXPORT_LEDGER,
        Action.EXPORT_PDF,
    ],

    "auditor": [
        Action.VIEW_TRANSACTION,
        Action.UPDATE_TRANSACTION_STATUS,
        Action.VERIFY_TRANSACTION,
        Action.EXPORT_TRANSACTIONS,
        Action.EXPORT_LEDGER,
    ],
}
