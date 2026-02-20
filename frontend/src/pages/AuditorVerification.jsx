import { useEffect, useState } from "react";
import api from "../services/api";
import { Link } from "react-router-dom";

export default function AuditorVerification() {
  const [docs, setDocs] = useState([]);
  const [ledger, setLedger] = useState([]);

  useEffect(() => {
    api.get("/alerts/compromised-documents")
      .then(res => setDocs(res.data))
      .catch(console.error);

    api.get("/ledger/all")
      .then(res => setLedger(res.data))
      .catch(console.error);
  }, []);

  const verifyDoc = async (id) => {
    try {
      await api.post("/action", null, {
        params: { doc_id: id, action: "VERIFY" }
      });
      alert("Document verified");
      window.location.reload();
    } catch {
      alert("Verify failed");
    }
  };

  const getLedgerForDoc = (docId) =>
    ledger.filter(l => l.document_id === docId);

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <h2 className="text-3xl font-bold mb-6">🕵️ Auditor Verification</h2>

      {/* Documents */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        {docs.map((d) => (
          <div key={d.id} className="bg-white rounded-xl shadow p-6 border">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-semibold text-lg">
                  TYPE: {d.doc_type} (#{d.id})
                </p>
                <p className="text-sm text-gray-600">Created at: {new Date(d.created_at).toLocaleDateString()}</p>
                <p className="text-sm text-gray-600">Owner: {d.owner_id}</p>
                <p className="text-sm text-gray-600">Number: {d.doc_number}</p>
                <p className="text-xs break-all text-gray-500 mt-2">
                  Hash: {d.file_hash}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  Issued at: {d.issued_at ? new Date(d.issued_at).toLocaleDateString() : "—"}
                </p>
              </div>

              <button
                onClick={() => verifyDoc(d.id)}
                className="bg-blue-600 text-white px-4 py-1.5 rounded hover:bg-blue-700"
              >
                Verify
              </button>
            </div>

            <span className="inline-block mt-3 text-xs px-2 py-1 bg-red-100 text-red-700 rounded">
              Integrity Failed
            </span>

            {/* Ledger table per document */}
            <div className="mt-6">
              <h4 className="font-semibold mb-2">Actor Action Document</h4>

              <div className="overflow-x-auto">
                <table className="w-full text-sm border">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="p-2 border">Actor</th>
                      <th className="p-2 border">Action</th>
                      <th className="p-2 border">Document</th>
                      <th className="p-2 border">Meta</th>
                      <th className="p-2 border">Created At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getLedgerForDoc(d.id).map((l, i) => (
                      <tr key={i} className="border-t">
                        <td className="p-2 border">{l.actor_id}</td>
                        <td className="p-2 border">{l.action}</td>
                        <td className="p-2 border">{l.document_id}</td>
                        <td className="p-2 border text-xs">
                          {JSON.stringify(l.extra_data || {})}
                        </td>
                        <td className="p-2 border">
                          {new Date(l.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <Link
              to={`/document/${d.id}`}
              className="inline-block mt-4 text-blue-600 text-sm hover:underline"
            >
              Open full document →
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}