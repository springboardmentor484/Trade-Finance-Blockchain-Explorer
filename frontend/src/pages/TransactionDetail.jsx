import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

export default function TransactionDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get(`/transaction?id=${id}`)
      .then(res => setData(res.data))
      .catch(() => alert("Failed to load transaction"));
  }, [id]);

  if (!data) return <div className="p-6 text-gray-600">Loading transaction details...</div>;

  const { transaction, documents, ledger } = data;

  const statusBadge = (status) => {
    if (status === "completed") return "bg-green-100 text-green-700 border-green-300";
    if (status === "in_progress") return "bg-yellow-100 text-yellow-700 border-yellow-300";
    if (status === "pending") return "bg-orange-100 text-orange-700 border-orange-300";
    if (status === "disputed") return "bg-red-100 text-red-700 border-red-300";
    return "bg-gray-100 text-gray-700 border-gray-300";
  };

  const docIcon = (type) => {
    if (type === "PO") return "📝";
    if (type === "BOL") return "📦";
    if (type === "INVOICE") return "🧾";
    if (type === "LOC") return "🏦";
    return "📄";
  };

  const actionDotColor = (action) => {
    if (action === "ISSUED") return "bg-blue-600";
    if (action === "VERIFIED") return "bg-purple-600";
    if (action === "SHIPPED") return "bg-orange-500";
    if (action === "RECEIVED") return "bg-green-600";
    if (action === "PAID") return "bg-emerald-600";
    return "bg-gray-400";
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 bg-gray-50 min-h-screen">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Transaction #{transaction.id}</h2>
          <p className="text-sm text-gray-500">
            End-to-end trade workflow, documents, and ledger trail
          </p>
        </div>

        <span
          className={`px-4 py-1.5 rounded-full text-sm font-semibold border ${statusBadge(transaction.status)}`}
        >
          {transaction.status.toUpperCase()}
        </span>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SummaryCard label="Buyer" value={transaction.buyer_name} color="blue" />
        <SummaryCard label="Seller" value={transaction.seller_name} color="indigo" />
        <SummaryCard label="Amount" value={`${transaction.amount} ${transaction.currency}`} color="emerald" />
      </div>

      {/* Documents */}
      <Card title="📄 Documents" accent="blue">
        {documents.length === 0 ? (
          <p className="text-gray-500">No documents uploaded yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map(doc => (
              <div
                key={doc.id}
                className="border-l-4 border-blue-500 rounded-lg p-4 bg-white hover:shadow transition flex items-center gap-3"
              >
                <div className="text-2xl">{docIcon(doc.doc_type)}</div>
                <div>
                  <p className="font-semibold">
                    {doc.doc_type}
                  </p>
                  <p className="text-sm text-gray-600">Status: {doc.status}</p>
                  <a
                    href={`http://127.0.0.1:8000/file?file_url=${doc.file_url}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-block mt-1 text-blue-600 text-sm underline"
                  >
                    Download File
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Ledger Timeline */}
      <Card title="🧾 Ledger Timeline" accent="purple">
        {ledger.length === 0 ? (
          <p className="text-gray-500">No ledger entries yet.</p>
        ) : (
          <div className="relative border-l-2 border-gray-300 pl-6 space-y-6">
            {ledger.map((entry, index) => (
              <div key={index} className="relative">
                {/* Dot */}
                <div
                  className={`absolute -left-[9px] top-1.5 h-4 w-4 rounded-full ${actionDotColor(entry.action)}`}
                />

                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <p className="font-medium">
                    {entry.action}
                  </p>

                  <p className="text-sm text-gray-700">
                    By {entry.actor_name} ({entry.actor_role}, {entry.actor_org})
                  </p>

                  <p className="text-xs text-gray-500">
                    {new Date(entry.created_at).toLocaleString()}
                  </p>

                  <div className="mt-2 text-sm text-gray-700 space-y-1">
                    {entry.extra_data?.transaction_id && (
                      <p>🔗 Transaction: #{entry.extra_data.transaction_id}</p>
                    )}
                    {entry.extra_data?.po_id && (
                      <p>📄 PO ID: #{entry.extra_data.po_id}</p>
                    )}
                    {entry.extra_data?.tracking_id && (
                      <p>📦 Tracking ID: {entry.extra_data.tracking_id}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function SummaryCard({ label, value, color }) {
  const colors = {
    blue: "border-blue-500",
    indigo: "border-indigo-500",
    emerald: "border-emerald-500",
  };

  return (
    <div className={`bg-white p-5 rounded-xl shadow border-l-4 ${colors[color]}`}>
      <p className="text-gray-500 text-sm">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}

function Card({ title, children, accent }) {
  const accents = {
    blue: "border-blue-500",
    purple: "border-purple-600",
  };

  return (
    <div className={`bg-white p-6 rounded-xl shadow border-l-4 ${accents[accent]}`}>
      <h3 className="text-xl font-semibold mb-4">{title}</h3>
      {children}
    </div>
  );
}
