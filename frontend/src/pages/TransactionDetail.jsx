import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

export default function TransactionDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    api.get(`/transaction?id=${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => setData(res.data))
      .catch(() => alert("Failed to load transaction"));
  }, [id]);

  if (!data) return <div className="p-6">Loading...</div>;

  const { transaction, documents, ledger } = data;

  // Build document ID -> document type map (PO, LOC, BOL, INVOICE)
  const docTypeMap = {};
  documents.forEach(doc => {
    docTypeMap[doc.id] = doc.doc_type;
  });

  return (
    <div className="p-6 space-y-6">

      {/* Transaction Info */}
      <div className="border rounded p-4">
        <h2 className="text-2xl font-semibold mb-2">
          Transaction #{transaction.id}
        </h2>

        <p>Buyer: {transaction.buyer_id}</p>
        <p>Seller: {transaction.seller_id}</p>
        <p>
          Amount: {transaction.amount} {transaction.currency}
        </p>

        <span
          className={`inline-block mt-2 px-3 py-1 rounded text-sm ${
            transaction.status === "completed"
              ? "bg-green-100 text-green-700"
              : transaction.status === "in_progress"
              ? "bg-yellow-100 text-yellow-700"
              : "bg-gray-100 text-gray-700"
          }`}
        >
          {transaction.status}
        </span>
      </div>

      {/* Documents */}
      <div className="border rounded p-4">
        <h3 className="text-xl font-semibold mb-3">Documents</h3>

        <ul className="space-y-2">
          {documents.map(doc => (
            <li key={doc.id} className="border p-2 rounded">
              <p className="font-medium">{doc.doc_type}</p>
              <p className="text-sm text-gray-600">Status: {doc.status}</p>

              <a
                href={`http://127.0.0.1:8000/file?file_url=${doc.file_url}`}
                target="_blank"
                rel="noreferrer"
                className="text-blue-600 text-sm underline"
              >
                Download
              </a>
            </li>
          ))}
        </ul>
      </div>

      {/* Ledger Timeline */}
      <div className="border rounded p-4">
        <h3 className="text-xl font-semibold mb-3">Ledger Timeline</h3>

        <div className="space-y-3">
          {ledger.map((entry, index) => {
            const docType = docTypeMap[entry.document_id] || "Document";

            return (
              <div
                key={index}
                className="border-l-4 border-blue-600 bg-gray-50 p-3 rounded"
              >
                <p className="font-medium">
                  {entry.action} – {docType}
                </p>

                {/* Actor info */}
                <p className="text-sm text-gray-700">
                    By {entry.actor_role} (User #{entry.actor_id})
                </p>


                <p className="text-xs text-gray-500">
                  {new Date(entry.created_at).toLocaleString()}
                </p>

                {/* Metadata */}
                <div className="text-sm text-gray-700 mt-1">
                  {entry.extra_data?.transaction_id && (
                    <p>Transaction: #{entry.extra_data.transaction_id}</p>
                  )}

                  {entry.extra_data?.po_id && (
                    <p>PO ID: #{entry.extra_data.po_id}</p>
                  )}

                  {entry.extra_data?.tracking_id && (
                    <p>Tracking ID: {entry.extra_data.tracking_id}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
