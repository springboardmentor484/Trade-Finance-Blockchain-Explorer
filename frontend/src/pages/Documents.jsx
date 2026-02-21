import { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function Documents() {
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    fetchDocuments();
  }, []);

  async function fetchDocuments() {
    const res = await apiFetch("/documents/");
    const data = await res.json();
    setDocs(data);
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Documents</h1>

      {docs.length === 0 && (
        <div>No documents found for this user.</div>
      )}

      {docs.map((d) => (
        <div key={d.id} className="border p-4 rounded mb-3">
          <div>ID: {d.id}</div>
          <div>Type: {d.doc_type}</div>
          <div>Status: {d.status}</div>
        </div>
      ))}
    </div>
  );
}
