// src/api/transactions.js
import { apiFetch } from "./index";

/* ===============================
   LIST TRANSACTIONS
================================= */
export async function fetchTransactions() {
  const res = await apiFetch("/transactions/");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch transactions");
  }

  return res.json();
}

/* ===============================
   CREATE TRANSACTION
================================= */
export async function createTransaction(
  buyerId,
  sellerId,
  amount,
  currency,
  description,
  lcNumber = null,
  lcIssuerId = null
) {
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

/* ===============================
   GET TRANSACTION DETAILS
================================= */
export async function fetchTransaction(transactionId) {
  const res = await apiFetch(`/transactions/${transactionId}`);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch transaction");
  }

  return res.json();
}

/* ===============================
   UPDATE TRANSACTION STATUS
   🔥 FIXED: Removed notes
================================= */
export async function updateTransactionStatus(transactionId, status) {
  const payload = { status };

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

/* ===============================
   GENERIC STEP EXECUTOR
================================= */
export async function executeTransactionStep(transactionId, stepName, payload = null) {
  const res = await apiFetch(
    `/transactions/${transactionId}/step/${stepName}`,
    {
      method: "POST",
      body: payload ? JSON.stringify(payload) : undefined,
    }
  );

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to execute step");
  }

  return res.json();
}

/* ===============================
   MARK DISPUTED
================================= */
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

/* ===============================
   FETCH RISK SUMMARY
   🔥 FIXED: Now returns parsed JSON
================================= */
export async function fetchRiskSummary() {
  const res = await apiFetch("/transactions/risk-summary");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch risk summary");
  }

  return res.json();
}