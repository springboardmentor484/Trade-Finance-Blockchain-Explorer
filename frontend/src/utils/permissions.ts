type Role = "bank" | "coperate" | "auditor" | "admin";
type Action = "ISSUED" | "SHIPPED" | "RECEIVED" | "VERIFY" | "PAID";
type DocType = "INVOICE" | "BOL" | "PO" | "LOC";

const ACTION_RULES: Record<
  DocType,
  Record<Action, Partial<Record<Role, Action[]>>>
> = {
  INVOICE: {
    ISSUED: {
      bank: ["PAID"],
      admin: ["PAID"],
    },
    PAID: {},
  },

  BOL: {
    ISSUED: {
      coperate: ["SHIPPED"],
      admin: ["SHIPPED"],
    },
    SHIPPED: {
      coperate: ["RECEIVED"],
      admin: ["RECEIVED"],
    },
    RECEIVED: {
      auditor: ["VERIFY"],
      admin: ["VERIFY"],
    },
    VERIFY: {},
  },

  PO: {
    ISSUED: {
      auditor: ["VERIFY"],
      admin: ["VERIFY"],
    },
    VERIFY: {},
  },

  LOC: {
    ISSUED: {
      auditor: ["VERIFY"],
      admin: ["VERIFY"],
    },
    VERIFY: {},
  },
};

export function getAllowedActions(
  docType: string,
  lastAction: string,
  role: string
): string[] {
  return (
    ACTION_RULES[docType as DocType]?.[lastAction as Action]?.[
      role as Role
    ] || []
  );
}