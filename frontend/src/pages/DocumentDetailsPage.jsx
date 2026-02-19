import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

function DocumentDetailsPage() {
  const { id } = useParams();
  const [doc, setDoc] = useState(null);

  useEffect(() => {
    // TODO: Replace with real API call
    setDoc({
      id,
      doc_number: "DOC-001",
      status: "ISSUED",
      ledger: [
        { id: 1, action: "ISSUED", actor_id: 3, created_at: "2026-01-01" },
      ],
      allowed_actions: ["ACCEPTED"],
    });
  }, [id]);

  if (!doc) return null;

  return (
    <div className="p-6">
      <Link className="text-blue-600" to="/documents">
        ← Back to documents
      </Link>

      <h1 className="text-2xl font-bold my-4">Document Details</h1>

      <div className="border p-4 rounded-xl shadow-sm">
        <div className="mb-2">
          <span className="font-semibold">Document:</span> {doc.doc_number}
        </div>
        <div className="mb-2">
          <span className="font-semibold">Status:</span> {doc.status}
        </div>

        <div className="mt-4">
          <h2 className="font-semibold">Ledger</h2>
          <div className="space-y-2 mt-2">
            {doc.ledger.map((entry) => (
              <div key={entry.id} className="border p-2 rounded-lg">
                {entry.action} by {entry.actor_id}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-4">
          <h2 className="font-semibold">Allowed Actions</h2>
          <div className="flex gap-2 mt-2">
            {doc.allowed_actions.map((action) => (
              <button
                key={action}
                className="px-4 py-2 border rounded-lg"
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DocumentDetailsPage;
