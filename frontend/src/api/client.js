const API_BASE = "http://127.0.0.1:8000";

export async function uploadDocument(formData, token) {
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function getDocuments(token) {
  const res = await fetch(`${API_BASE}/documents`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}