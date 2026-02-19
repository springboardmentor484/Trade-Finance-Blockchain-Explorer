// src/api/analytics.js

import { apiFetch } from "./index";

/* =====================================================
   DOCUMENT ANALYTICS
===================================================== */
export async function fetchDocumentAnalytics() {
  const res = await apiFetch("/analytics/documents/summary");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch document analytics");
  }

  return res.json();
}

/* =====================================================
   TRANSACTION ANALYTICS
===================================================== */
export async function fetchTransactionAnalytics() {
  const res = await apiFetch("/analytics/transactions/summary");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch transaction analytics");
  }

  return res.json();
}

/* =====================================================
   ORG DASHBOARD SUMMARY
===================================================== */
export async function fetchOrgDashboardSummary() {
  const res = await apiFetch("/analytics/org/dashboard");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch org dashboard summary");
  }

  return res.json();
}

/* =====================================================
   ORG TRANSACTION TIMELINE
===================================================== */
export async function fetchOrgTransactionTimeline() {
  const res = await apiFetch("/analytics/org/timeline");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch org transaction timeline");
  }

  return res.json();
}

/* =====================================================
   EXPORT DOCUMENTS CSV
===================================================== */
export async function exportDocumentsCSV() {
  const res = await apiFetch("/exports/documents/csv");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export documents CSV");
  }

  return res.blob();
}

/* =====================================================
   EXPORT TRANSACTIONS CSV
===================================================== */
export async function exportTransactionsCSV() {
  const res = await apiFetch("/exports/transactions/csv");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export transactions CSV");
  }

  return res.blob();
}

/* =====================================================
   EXPORT DOCUMENTS PDF
===================================================== */
export async function exportDocumentsPDF() {
  const res = await apiFetch("/exports/documents/pdf");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export documents PDF");
  }

  return res.blob();
}

/* =====================================================
   EXPORT TRANSACTIONS PDF
===================================================== */
export async function exportTransactionsPDF() {
  const res = await apiFetch("/exports/transactions/pdf");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export transactions PDF");
  }

  return res.blob();
}

/* =====================================================
   EXPORT LEDGER CSV
===================================================== */
export async function exportLedgerCSV() {
  const res = await apiFetch("/exports/ledger/csv");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export ledger");
  }

  return res.blob();
}

/* =====================================================
   EXPORT SINGLE TRANSACTION PDF
===================================================== */
export async function exportTransactionPDF(id) {
  const res = await apiFetch(`/exports/transactions/${id}/pdf`);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export transaction PDF");
  }

  return res.blob();
}

/* =====================================================
   ACTIVITY LOG
===================================================== */
export async function fetchActivityLog(days = 30) {
  const res = await apiFetch(`/analytics/ledger/activity?days=${days}`);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch activity log");
  }

  return res.json();
}

/* =====================================================
   DASHBOARD KPIs
===================================================== */
export async function fetchDashboardKPIs() {
  const res = await apiFetch("/analytics/dashboard/kpis");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch KPIs");
  }

  return res.json();
}

/* =====================================================
   DOWNLOAD HELPERS
===================================================== */
export function downloadCSV(blob, filename = "export.csv") {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export function downloadPDF(blob, filename = "export.pdf") {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export async function downloadFile(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}