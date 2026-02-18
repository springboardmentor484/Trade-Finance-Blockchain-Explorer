export const ACTION_RULES: Record<
  string,
  Record<string, Record<string, string[]>>
> = {
  PO: {
    ISSUED: {
      auditor: ["VERIFY"],
      bank: ["ISSUE_LOC"],
    },
    VERIFY: {},
  },

  LOC: {
    ISSUED: {
      auditor: ["VERIFY"],
    },
    VERIFY: {},
  },

  BOL: {
    ISSUED: {
      seller: ["SHIPPED"],
    },
    SHIPPED: {
      coperate: ["RECEIVED"],
    },
    RECEIVED: {},
  },

  INVOICE: {
    ISSUED: {
      bank: ["PAID"],
    },
  },
};