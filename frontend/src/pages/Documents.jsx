import { useEffect, useState } from "react";
import api from "../services/api";

export default function Documents() {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    api.get("/documents", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    .then(res => setDocuments(res.data))
    .catch(() => alert("Unauthorized"));
  }, []);

  return (
    <div>
      <h2>My Documents</h2>

      <ul>
        {documents.map(doc => (
          <li key={doc.id}>
            <a href={`/document/${doc.id}`}>
              {doc.doc_number} - {doc.status}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
