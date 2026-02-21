import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function DocumentsPage() {
  const [docs, setDocs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // TODO: Replace with real API call
    setDocs([
      { id: 1, doc_number: "DOC-001", status: "ISSUED" },
      { id: 2, doc_number: "DOC-002", status: "ACCEPTED" },
    ]);
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Documents</h1>

      <div className="grid gap-4">
        {docs.map((doc) => (
          <div
            key={doc.id}
            className="border p-4 rounded-xl shadow-sm hover:shadow-lg cursor-pointer"
            onClick={() => navigate(`/documents/${doc.id}`)}
          >
            <div className="flex justify-between">
              <div className="font-semibold">{doc.doc_number}</div>
              <div className="text-sm text-gray-500">{doc.status}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DocumentsPage;
