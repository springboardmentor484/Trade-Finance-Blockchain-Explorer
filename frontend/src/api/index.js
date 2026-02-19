// src/api/index.js

import { getToken } from "./auth";

const BASE = "http://127.0.0.1:8000";

/**
 * Central API fetch wrapper
 * Automatically attaches Authorization header
 */
export async function apiFetch(path, options = {}) {
  const token = getToken();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return fetch(`${BASE}${path}`, {
    ...options,
    headers,
  });
}

// Re-export auth helpers
export { setToken, getToken, clearToken } from "./auth";
