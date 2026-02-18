ACCESS_CONTROL = {
    ("BUYER", "BOL"): {"RECEIVED"},

    ("SELLER", "BOL"): {"SHIPPED", "ISSUE_INVOICE"},
    ("SELLER", "PO"): {"ISSUE_BOL"},

    ("AUDITOR", "PO"): {"VERIFY"},
    ("AUDITOR", "LOC"): {"VERIFY"},

    ("BANK", "INVOICE"): {"PAID"},
    ("BANK", "LOC"): {"ISSUE_LOC"},
}

def validate_action(role: str, document_type: str, action: str) -> bool:
    return action in ACCESS_CONTROL.get((role, document_type), set())
