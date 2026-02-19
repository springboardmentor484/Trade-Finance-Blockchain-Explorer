// src/api/transactions.js

import { apiFetch } from "./index";

// 🔹 LIST TRANSACTIONS
export async function fetchTransactions() {
  const res = await apiFetch("/transactions/");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch transactions");
  }

  return res.json();
}

// 🔹 CREATE TRANSACTION
export async function createTransaction(buyerId, sellerId, amount, currency, description, lcNumber = null, lcIssuerId = null) {
  const payload = {
    buyer_id: buyerId,
    seller_id: sellerId,
    amount,
    currency,
    description,
    lc_number: lcNumber,
    lc_issuer_id: lcIssuerId,
  };

  const res = await apiFetch("/transactions/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to create transaction");
  }

  return res.json();
}

// 🔹 GET TRANSACTION DETAILS
export async function fetchTransaction(transactionId) {
  const res = await apiFetch(`/transactions/${transactionId}`);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch transaction");
  }

  return res.json();
}

// 🔹 UPDATE TRANSACTION STATUS
export async function updateTransactionStatus(transactionId, status, notes = null) {
  const payload = {
    status,
    notes,
  };

  const res = await apiFetch(`/transactions/${transactionId}/status`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to update transaction");
  }

  return res.json();
}

// 🔹 GET RISK SUMMARY
export async function fetchRiskSummary() {
  const res = await apiFetch("/transactions/analytics/risk-summary");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch risk summary");
  }

  return res.json();
}
// ===== TRADE TRANSACTION FLOW (7 STEPS) =====

// STEP 1: Create PO
export async function step1CreatePO(transactionId) {
  const res = await apiFetch(`/transactions/${transactionId}/step/create-po`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to create PO");
  }

  return res.json();
}

// STEP 2: Issue LOC
export async function step2IssueLOC(transactionId) {
  const res = await apiFetch(`/transactions/${transactionId}/step/issue-loc`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to issue LOC");
  }

  return res.json();
}

// STEP 3: Verify
export async function step3Verify(transactionId) {
  const res = await apiFetch(`/transactions/${transactionId}/step/verify`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to verify transaction");
  }

  return res.json();
}

// STEP 7: Mark Completed
export async function step7MarkCompleted(transactionId) {
  const res = await apiFetch(`/transactions/${transactionId}/step/mark-completed`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to mark transaction as completed");
  }

  return res.json();
}

// Mark as Disputed
export async function markDisputed(transactionId, reason = null) {
  const payload = { reason };

  const res = await apiFetch(`/transactions/${transactionId}/mark-disputed`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to mark transaction as disputed");
  }

  return res.json();
}