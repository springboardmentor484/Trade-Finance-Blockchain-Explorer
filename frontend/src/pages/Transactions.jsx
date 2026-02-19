import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  fetchTransactions,
  createTransaction,
  fetchRiskSummary,
} from "../api/transactions";
import { apiFetch } from "../api";

export default function Transactions() {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [riskSummary, setRiskSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [userInfo, setUserInfo] = useState(null);
  const [ledgerEntries, setLedgerEntries] = useState([]);
  const [loadingLedger, setLoadingLedger] = useState(false);
  const [formData, setFormData] = useState({
    buyer_id: "",
    seller_id: "",
    amount: "",
    currency: "USD",
    description: "",
    lc_number: "",
    lc_issuer_id: "",
  });

  useEffect(() => {
    loadData();
  }, []);

  // Fetch ledger entries when audit logs tab is clicked
  useEffect(() => {
    if (activeTab === "audit_logs") {
      fetchLedgerEntries();
    }
  }, [activeTab]);

  async function fetchLedgerEntries() {
    try {
      setLoadingLedger(true);
      const response = await apiFetch("/analytics/ledger/activity?days=90");
      const data = await response.json();
      if (response.ok) {
        setLedgerEntries(data.activities || []);
      }
    } catch (err) {
      console.error("Failed to fetch ledger entries:", err);
      setError(err.message);
    } finally {
      setLoadingLedger(false);
    }
  }

  async function loadData() {
    try {
      setLoading(true);
      
      // Fetch user profile
      const userResponse = await apiFetch("/users/");
      const userData = await userResponse.json();
      if (userResponse.ok) {
        setUserInfo(userData);
      }
      
      // Fetch transactions and risk summary
      const [txns, risk] = await Promise.all([
        fetchTransactions(),
        fetchRiskSummary(),
      ]);
      setTransactions(txns);
      setRiskSummary(risk);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateTransaction(e) {
    e.preventDefault();
    try {
      await createTransaction(
        parseInt(formData.buyer_id),
        parseInt(formData.seller_id),
        parseFloat(formData.amount),
        formData.currency,
        formData.description,
        formData.lc_number || null,
        formData.lc_issuer_id ? parseInt(formData.lc_issuer_id) : null
      );
      setShowCreateForm(false);
      setFormData({
        buyer_id: "",
        seller_id: "",
        amount: "",
        currency: "USD",
        description: "",
        lc_number: "",
        lc_issuer_id: "",
      });
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  const getStatusColor = (status) => {
    switch(status) {
      case "PENDING":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "IN_PROGRESS":
        return "bg-blue-100 text-blue-800 border-blue-300";
      case "COMPLETED":
        return "bg-green-100 text-green-800 border-green-300";
      case "DISPUTED":
        return "bg-red-100 text-red-800 border-red-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getRiskColor = (score) => {
    if (score < 20) return "text-green-600 bg-green-50";
    if (score < 40) return "text-yellow-600 bg-yellow-50";
    if (score < 60) return "text-orange-600 bg-orange-50";
    return "text-red-600 bg-red-50";
  };

  const getRiskLevel = (score) => {
    if (score < 20) return "LOW";
    if (score < 40) return "MEDIUM";
    if (score < 60) return "HIGH";
    return "CRITICAL";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Gradient Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">📊 Trade Transactions</h1>
              <p className="text-blue-100">Manage and track all trade transactions and activities</p>
            </div>
            {userInfo && (
              <div className="text-right text-blue-100">
                <p className="text-sm">Logged in as:</p>
                <p className="font-semibold text-white">{userInfo.name}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`pb-3 font-semibold border-b-2 transition ${
                activeTab === "dashboard"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              📊 Dashboard
            </button>
            <button
              onClick={() => setActiveTab("audit_logs")}
              className={`pb-3 font-semibold border-b-2 transition ${
                activeTab === "audit_logs"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              📋 Audit Logs
            </button>
            <button
              onClick={() => setActiveTab("transactions")}
              className={`pb-3 font-semibold border-b-2 transition ${
                activeTab === "transactions"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              📈 Transactions
            </button>
            <button
              onClick={() => navigate("/documents")}
              className="pb-3 font-semibold text-gray-600 hover:text-gray-900 transition ml-auto"
            >
              📄 Documents
            </button>
            <button
              onClick={() => {
                localStorage.clear();
                navigate("/login");
              }}
              className="pb-3 font-semibold text-gray-600 hover:text-gray-900 transition"
            >
              🚪 Logout
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-600 rounded">
            <p className="text-red-700 font-semibold">{error}</p>
          </div>
        )}

        {/* DASHBOARD TAB */}
        {activeTab === "dashboard" && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard Overview</h2>

            {/* Risk Summary Cards */}
            {riskSummary && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
              <div className="text-gray-600 text-sm font-semibold uppercase">Total Transactions</div>
              <div className="text-3xl font-bold text-gray-900 mt-2">{riskSummary.total_transactions}</div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border-l-4 border-purple-500">
              <div className="text-gray-600 text-sm font-semibold uppercase">Total Volume</div>
              <div className="text-3xl font-bold text-gray-900 mt-2">₹{(riskSummary.total_volume / 100000).toFixed(1)}L</div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border-l-4 border-yellow-500">
              <div className="text-gray-600 text-sm font-semibold uppercase">Average Risk</div>
              <div className={`text-3xl font-bold mt-2 ${
                riskSummary.average_risk_score < 20 ? "text-green-600" :
                riskSummary.average_risk_score < 40 ? "text-yellow-600" :
                riskSummary.average_risk_score < 60 ? "text-orange-600" :
                "text-red-600"
              }`}>
                {riskSummary.average_risk_score.toFixed(0)}/100
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border-l-4 border-red-500">
              <div className="text-gray-600 text-sm font-semibold uppercase">High Risk</div>
              <div className="text-3xl font-bold text-red-600 mt-2">{riskSummary.high_risk_count}</div>
            </div>
          </div>
            )}
          </div>
        )}

        {/* AUDIT LOGS TAB */}
        {activeTab === "audit_logs" && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">📋 Audit Logs & Ledger</h2>
            {loadingLedger ? (
              <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
                <p>Loading ledger entries...</p>
              </div>
            ) : ledgerEntries.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
                <p className="text-lg mb-2">📋 No Ledger Entries</p>
                <p className="text-sm">All transaction actions and changes are logged here for compliance and tracking purposes.</p>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
                <table className="w-full">
                  <thead className="bg-gray-100 border-b-2 border-gray-300">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Timestamp</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Action</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Document ID</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actor ID</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ledgerEntries.map((entry) => (
                      <tr key={entry.id} className="border-b border-gray-200 hover:bg-gray-50">
                        <td className="px-6 py-3 text-sm text-gray-700">
                          {new Date(entry.timestamp).toLocaleString()}
                        </td>
                        <td className="px-6 py-3 text-sm font-semibold">
                          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700">
                            {entry.action}
                          </span>
                        </td>
                        <td className="px-6 py-3 text-sm text-gray-700">
                          Doc #{entry.document_id}
                        </td>
                        <td className="px-6 py-3 text-sm text-gray-700">
                          User #{entry.actor_id}
                        </td>
                        <td className="px-6 py-3 text-sm text-gray-600">
                          {entry.meta ? JSON.stringify(entry.meta) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TRANSACTIONS TAB */}
        {activeTab === "transactions" && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">All Transactions</h2>

            {/* Create Button */}
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Manage Transactions</h3>
              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-teal-600 text-white px-6 py-2 rounded-lg hover:bg-teal-700 font-semibold transition"
              >
                ➕ New Transaction
              </button>
            </div>

            {/* Create Transaction Form */}
            {showCreateForm && (
              <div className="bg-white p-6 rounded-lg shadow mb-6 border border-gray-200">
                <h2 className="text-lg font-bold mb-4 text-gray-900">Create Trade Transaction</h2>
                <form onSubmit={handleCreateTransaction} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <input
                      type="number"
                      placeholder="Buyer ID"
                      value={formData.buyer_id}
                      onChange={(e) =>
                        setFormData({ ...formData, buyer_id: e.target.value })
                      }
                      className="border border-gray-300 p-3 rounded"
                      required
                    />
                    <input
                      type="number"
                      placeholder="Seller ID"
                      value={formData.seller_id}
                      onChange={(e) =>
                        setFormData({ ...formData, seller_id: e.target.value })
                      }
                      className="border border-gray-300 p-3 rounded"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <input
                      type="number"
                      step="0.01"
                      placeholder="Amount"
                      value={formData.amount}
                      onChange={(e) =>
                        setFormData({ ...formData, amount: e.target.value })
                      }
                      className="border border-gray-300 p-3 rounded"
                      required
                    />
                    <select
                      value={formData.currency}
                      onChange={(e) =>
                        setFormData({ ...formData, currency: e.target.value })
                      }
                      className="border border-gray-300 p-3 rounded"
                    >
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="INR">INR</option>
                      <option value="CNY">CNY</option>
                    </select>
                  </div>
                  <textarea
                    placeholder="Description"
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    className="border border-gray-300 p-3 rounded w-full"
                    required
                  />
                  <div className="grid grid-cols-2 gap-4">
                    <input
                      type="text"
                      placeholder="LC Number (optional)"
                      value={formData.lc_number}
                      onChange={(e) =>
                        setFormData({ ...formData, lc_number: e.target.value })
                      }
                      className="border border-gray-300 p-3 rounded"
                    />
                    <input
                      type="number"
                      placeholder="LC Issuer ID (optional)"
                      value={formData.lc_issuer_id}
                      onChange={(e) =>
                        setFormData({ ...formData, lc_issuer_id: e.target.value })
                      }
                      className="border border-gray-300 p-3 rounded"
                    />
                  </div>
                  <div className="flex gap-3">
                    <button
                      type="submit"
                      className="bg-teal-600 text-white px-6 py-2 rounded hover:bg-teal-700 font-semibold transition"
                    >
                      ✔️ Create Transaction
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateForm(false)}
                      className="bg-gray-400 text-white px-6 py-2 rounded hover:bg-gray-500 font-semibold transition"
                    >
                      ✕ Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Transactions Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              {transactions.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-100 border-b">
                      <tr>
                        <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">ID</th>
                        <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Buyer</th>
                        <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Seller</th>
                        <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Amount</th>
                        <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Status</th>
                        <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Risk</th>
                        <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Created</th>
                        <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transactions.map((tx) => (
                        <tr key={tx.id} className="border-b hover:bg-gray-50 transition">
                          <td className="px-6 py-4 text-sm font-bold text-gray-900">{tx.id}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{tx.buyer_id}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{tx.seller_id}</td>
                          <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                            ₹ {tx.amount.toLocaleString("en-IN", {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(tx.status)}`}>
                              {tx.status}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getRiskColor(tx.risk_score)}`}>
                              {getRiskLevel(tx.risk_score)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {new Date(tx.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4">
                            <button
                              onClick={() => navigate(`/transactions/${tx.id}`)}
                              className="text-blue-600 hover:text-blue-800 font-semibold text-sm"
                            >
                              View Details →
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">No transactions yet</p>
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="mt-4 text-teal-600 hover:underline font-semibold"
                  >
                    Create a transaction to get started
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

