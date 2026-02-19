import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchTransaction } from "../api/transactions";

export default function TransactionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("details");

  useEffect(() => {
    loadTransaction();
  }, [id]);

  async function loadTransaction() {
    try {
      setLoading(true);
      const data = await fetchTransaction(id);
      setTransaction(data);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="p-6">Loading transaction...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error}</div>;
  if (!transaction) return <div className="p-6">Transaction not found</div>;

  const statusColor = {
    PENDING: "bg-yellow-100 text-yellow-800 border-yellow-300",
    IN_PROGRESS: "bg-blue-100 text-blue-800 border-blue-300",
    COMPLETED: "bg-green-100 text-green-800 border-green-300",
    DISPUTED: "bg-red-100 text-red-800 border-red-300",
    CANCELLED: "bg-gray-100 text-gray-800 border-gray-300",
  };

  const statusBg = statusColor[transaction.status] || "bg-gray-100 text-gray-800";

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Navigation Tabs */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Trade Transactions</h1>
              <p className="text-gray-600 mt-1">Transaction ID: {id}</p>
            </div>
            <button
              onClick={() => navigate("/transactions")}
              className="text-blue-600 hover:text-blue-800 font-semibold"
            >
              ← Back to List
            </button>
          </div>

          {/* Navigation Tabs */}
          <div className="flex space-x-8 border-t pt-3">
            <button
              onClick={() => setActiveTab("details")}
              className={`pb-3 font-semibold border-b-2 transition ${
                activeTab === "details"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              📋 Details
            </button>
            <button
              onClick={() => setActiveTab("ledger")}
              className={`pb-3 font-semibold border-b-2 transition ${
                activeTab === "ledger"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              📊 Ledger Entries
            </button>
            <button
              onClick={() => setActiveTab("documents")}
              className={`pb-3 font-semibold border-b-2 transition ${
                activeTab === "documents"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              📄 Documents
            </button>
          </div>
        </div>
      </div>

      {/* User Info Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 py-2 flex items-center space-x-4 text-sm">
          <span className="text-gray-600">Logged in as:</span>
          <span className="font-semibold text-gray-900">admin@example.com</span>
          <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-semibold">
            Admin
          </span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* DETAILS TAB */}
        {activeTab === "details" && (
          <div className="space-y-6">
            {/* Transaction Main Card */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Transaction Information</h2>
                <div className={`px-4 py-2 rounded-lg border font-semibold text-lg ${statusBg}`}>
                  {transaction.status}
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
                {/* Transaction ID */}
                <div>
                  <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                    Transaction ID
                  </label>
                  <p className="text-gray-900 text-lg font-bold mt-1">{transaction.id}</p>
                </div>

                {/* Buyer */}
                <div>
                  <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                    Buyer ID
                  </label>
                  <p className="text-gray-900 text-lg font-bold mt-1">{transaction.buyer_id}</p>
                </div>

                {/* Seller */}
                <div>
                  <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                    Seller ID
                  </label>
                  <p className="text-gray-900 text-lg font-bold mt-1">{transaction.seller_id}</p>
                </div>

                {/* Amount */}
                <div>
                  <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                    Amount
                  </label>
                  <p className="text-gray-900 text-lg font-bold mt-1">
                    ₹ {transaction.amount.toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>

                {/* Currency */}
                <div>
                  <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                    Currency
                  </label>
                  <p className="text-gray-900 text-lg font-bold mt-1">{transaction.currency}</p>
                </div>

                {/* Risk Score */}
                <div>
                  <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                    Risk Score
                  </label>
                  <div className="mt-1 flex items-center space-x-2">
                    <div className="text-lg font-bold text-gray-900">{transaction.risk_score.toFixed(1)}/100</div>
                    <div className={`px-2 py-1 rounded text-xs font-semibold ${
                      transaction.risk_score < 20 ? "bg-green-100 text-green-800" :
                      transaction.risk_score < 40 ? "bg-yellow-100 text-yellow-800" :
                      transaction.risk_score < 60 ? "bg-orange-100 text-orange-800" :
                      "bg-red-100 text-red-800"
                    }`}>
                      {transaction.risk_score < 20 ? "LOW" :
                       transaction.risk_score < 40 ? "MEDIUM" :
                       transaction.risk_score < 60 ? "HIGH" :
                       "CRITICAL"}
                    </div>
                  </div>
                </div>

                {/* Created At */}
                <div>
                  <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                    Created At
                  </label>
                  <p className="text-gray-900 text-lg font-bold mt-1">
                    {new Date(transaction.created_at).toLocaleString()}
                  </p>
                </div>

                {/* Updated At */}
                <div>
                  <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                    Updated At
                  </label>
                  <p className="text-gray-900 text-lg font-bold mt-1">
                    {new Date(transaction.updated_at).toLocaleString()}
                  </p>
                </div>

                {/* Description */}
                <div className="col-span-2 md:col-span-3">
                  <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                    Description
                  </label>
                  <p className="text-gray-900 text-lg mt-1">{transaction.description}</p>
                </div>
              </div>
            </div>

            {/* Risk Factors Card */}
            {transaction.risk_factors && Object.keys(transaction.risk_factors).length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Risk Factors Analysis</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(transaction.risk_factors).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-gray-600 text-sm uppercase font-semibold">{key}</div>
                      <div className="text-gray-900 font-bold text-lg mt-1">
                        {typeof value === "object" ? JSON.stringify(value) : String(value)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-4">
              <button className="flex-1 bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-3 px-6 rounded-lg transition">
                📦 Shipped
              </button>
              <button className="flex-1 bg-purple-500 hover:bg-purple-600 text-white font-bold py-3 px-6 rounded-lg transition">
                📄 Invoice
              </button>
            </div>
          </div>
        )}

        {/* LEDGER ENTRIES TAB */}
        {activeTab === "ledger" && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold text-gray-900">📊 Ledger Entries - Transaction Audit Trail</h2>
              <p className="text-gray-600 mt-2">Complete immutable transaction history</p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100 border-b">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">ID</th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Actor ID</th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Action</th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Document ID</th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Metadata</th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {transaction.ledger_entries && transaction.ledger_entries.length > 0 ? (
                    transaction.ledger_entries.map((entry, idx) => (
                      <tr key={idx} className="border-b hover:bg-gray-50 transition">
                        <td className="px-6 py-4 text-sm text-gray-900 font-bold">{entry.id}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{entry.actor_id}</td>
                        <td className="px-6 py-4">
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                            {entry.action}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{entry.document_id || "—"}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          <code className="bg-gray-100 px-2 py-1 rounded text-xs">
                            {JSON.stringify(entry.meta).substring(0, 50)}...
                          </code>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {new Date(entry.timestamp).toLocaleString()}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                        No ledger entries found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* DOCUMENTS TAB */}
        {activeTab === "documents" && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">📄 Associated Documents</h2>
            <p className="text-gray-600 text-center py-8">
              No documents currently linked to this transaction. Documents will appear here as they are created.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
