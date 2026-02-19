const BASE = "http://127.0.0.1:8000";

export async function getAllowedActions(docId, token) {
  const res = await fetch(`${BASE}/documents/${docId}/allowed-actions`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.json();
}

export async function performAction(docId, action, token) {
  const res = await fetch(`${BASE}/documents/${docId}/action`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ action }),
  });
  return res.json();
}
