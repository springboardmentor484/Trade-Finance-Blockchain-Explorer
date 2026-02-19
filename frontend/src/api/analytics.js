// src/api/analytics.js

import { apiFetch } from "./index";

// 🔹 DOCUMENT ANALYTICS
export async function fetchDocumentAnalytics() {
  const res = await apiFetch("/analytics/documents/summary");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch document analytics");
  }

  return res.json();
}

// 🔹 TRANSACTION ANALYTICS
export async function fetchTransactionAnalytics() {
  const res = await apiFetch("/analytics/transactions/summary");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch transaction analytics");
  }

  return res.json();
}

// 🔹 EXPORT DOCUMENTS AS CSV
export async function exportDocumentsCSV() {
  const res = await apiFetch("/analytics/export/documents/csv");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export documents");
  }

  return res.json();
}

// 🔹 EXPORT TRANSACTIONS AS CSV
export async function exportTransactionsCSV() {
  const res = await apiFetch("/analytics/export/transactions/csv");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export transactions");
  }

  return res.json();
}

// 🔹 GET ACTIVITY LOG
export async function fetchActivityLog(days = 30) {
  const res = await apiFetch(`/analytics/ledger/activity?days=${days}`);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch activity log");
  }

  return res.json();
}

// 🔹 GET DASHBOARD KPIs
export async function fetchDashboardKPIs() {
  const res = await apiFetch("/analytics/dashboard/kpis");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch KPIs");
  }

  return res.json();
}

// 🔹 DOWNLOAD CSV
export async function downloadCSV(content, filename) {
  const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
// 🔹 ORG-LEVEL DASHBOARD
export async function fetchOrgDashboardSummary() {
  const res = await apiFetch("/analytics/org/dashboard/summary");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch org dashboard");
  }

  return res.json();
}

// 🔹 ORG TRANSACTION TIMELINE
export async function fetchOrgTransactionTimeline() {
  const res = await apiFetch("/analytics/org/dashboard/timeline");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch org timeline");
  }

  return res.json();
}

// 🔹 EXPORT DOCUMENTS AS PDF
export async function exportDocumentsPDF() {
  const res = await apiFetch("/analytics/export/documents/pdf");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export documents as PDF");
  }

  return res.json();
}

// 🔹 EXPORT TRANSACTIONS AS PDF
export async function exportTransactionsPDF() {
  const res = await apiFetch("/analytics/export/transactions/pdf");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to export transactions as PDF");
  }

  return res.json();
}

// 🔹 DOWNLOAD PDF
export async function downloadPDF(hexContent, filename) {
  const binaryString = atob(Buffer.from(hexContent, 'hex').toString('base64'));
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  const blob = new Blob([bytes], { type: "application/pdf" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}