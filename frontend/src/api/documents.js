// src/api/documents.js

import { apiFetch } from "./index";

// 🔹 LIST DOCUMENTS
export async function fetchDocuments() {
  const res = await apiFetch("/documents/");

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch documents");
  }

  return res.json();
}

// 🔹 UPLOAD DOCUMENT
export async function uploadDocument(docType, docNumber, file) {
  const formData = new FormData();
  formData.append("doc_type", docType);
  formData.append("doc_number", docNumber);
  formData.append("file", file);

  const token = localStorage.getItem("access_token");
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch("http://127.0.0.1:8000/documents/", {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to upload document");
  }

  return res.json();
}

// 🔹 SINGLE READ MODEL (document + ledger + allowed_actions)
export async function fetchDocumentRead(docId) {
  const res = await apiFetch(`/documents/${docId}/read`);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch document");
  }

  return res.json();
}

// 🔹 VERIFY DOCUMENT INTEGRITY
export async function verifyDocument(docId) {
  const res = await apiFetch(`/documents/${docId}/verify`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Verification failed");
  }

  return res.json();
}

// 🔹 GET FULL LEDGER
export async function fetchLedger(docId = null, action = null) {
  let url = "/documents/ledger/all";
  const params = new URLSearchParams();
  if (docId) params.append("doc_id", docId);
  if (action) params.append("action", action);
  if (params.toString()) url += "?" + params.toString();

  const res = await apiFetch(url);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch ledger");
  }

  return res.json();
}

// 🔹 PERFORM DOCUMENT ACTION
export async function performDocumentAction(docId, action, meta = {}) {
  const res = await apiFetch(`/documents/${docId}/action`, {
    method: "POST",
    body: JSON.stringify({ action, meta }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Action failed");
  }

  return res.json();
}

// 🔹 DOWNLOAD FILE
export async function downloadFile(docId) {
  const token = localStorage.getItem("access_token");
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`http://127.0.0.1:8000/documents/${docId}/file`, {
    method: "GET",
    headers,
  });

  if (!res.ok) {
    throw new Error("Failed to download file");
  }

  return res.blob();
}
