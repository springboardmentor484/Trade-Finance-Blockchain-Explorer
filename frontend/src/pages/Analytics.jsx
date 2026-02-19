import { useEffect, useState } from "react";
import {
  fetchDocumentAnalytics,
  fetchTransactionAnalytics,
  fetchDashboardKPIs,
  fetchActivityLog,
  exportDocumentsCSV,
  exportTransactionsCSV,
  exportDocumentsPDF,
  exportTransactionsPDF,
  downloadCSV,
  downloadPDF,
  fetchOrgDashboardSummary,
  fetchOrgTransactionTimeline,
} from "../api/analytics";

export default function Analytics() {
  const [orgDashboard, setOrgDashboard] = useState(null);
  const [orgTimeline, setOrgTimeline] = useState(null);
  const [documentAnalytics, setDocumentAnalytics] = useState(null);
  const [transactionAnalytics, setTransactionAnalytics] = useState(null);
  const [kpis, setKpis] = useState(null);
  const [activityLog, setActivityLog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  async function loadAnalytics() {
    try {
      setLoading(true);
      const [docs, txns, kpiData, activity, org, timeline] = await Promise.all([
        fetchDocumentAnalytics(),
        fetchTransactionAnalytics(),
        fetchDashboardKPIs(),
        fetchActivityLog(30),
        fetchOrgDashboardSummary(),
        fetchOrgTransactionTimeline(),
      ]);
      setDocumentAnalytics(docs);
      setTransactionAnalytics(txns);
      setKpis(kpiData);
      setActivityLog(activity);
      setOrgDashboard(org);
      setOrgTimeline(timeline);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleExportDocumentsCSV() {
    try {
      setExporting("documents-csv");
      const result = await exportDocumentsCSV();
      downloadCSV(result.content, result.filename);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting(null);
    }
  }

  async function handleExportTransactionsCSV() {
    try {
      setExporting("transactions-csv");
      const result = await exportTransactionsCSV();
      downloadCSV(result.content, result.filename);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting(null);
    }
  }

  async function handleExportDocumentsPDF() {
    try {
      setExporting("documents-pdf");
      const result = await exportDocumentsPDF();
      downloadPDF(result.content, result.filename);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting(null);
    }
  }

  async function handleExportTransactionsPDF() {
    try {
      setExporting("transactions-pdf");
      const result = await exportTransactionsPDF();
      downloadPDF(result.content, result.filename);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting(null);
    }
  }

  if (loading) return <div className="p-6">Loading Analytics...</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">Trade Finance Analytics</h1>
        <p className="text-gray-600 mt-1">Real-time compliance metrics & KPIs</p>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>
      )}

      {/* ORG-LEVEL SUMMARY */}
      {orgDashboard && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Organization Dashboard</h2>
          
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
              <div className="text-gray-500 text-sm font-semibold">Total Amount</div>
              <div className="text-3xl font-bold text-gray-900">
                ${(orgDashboard.summary.total_transaction_amount / 1000).toFixed(1)}K
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
              <div className="text-gray-500 text-sm font-semibold">Total Bought</div>
              <div className="text-3xl font-bold text-gray-900">
                ${(orgDashboard.summary.total_bought / 1000).toFixed(1)}K
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border-l-4 border-purple-500">
              <div className="text-gray-500 text-sm font-semibold">Total Sold</div>
              <div className="text-3xl font-bold text-gray-900">
                ${(orgDashboard.summary.total_sold / 1000).toFixed(1)}K
              </div>
            </div>
          </div>

          {/* Status Breakdown Pie Chart */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">Transaction Status</h3>
              <div className="space-y-3">
                {Object.entries(orgDashboard.status_breakdown).map(([status, count]) => (
                  <div key={status}>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-700">{status}</span>
                      <span className="font-semibold">{count}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          status === 'COMPLETED' ? 'bg-green-500' :
                          status === 'DISPUTED' ? 'bg-red-500' :
                          status === 'IN_PROGRESS' ? 'bg-yellow-500' :
                          'bg-blue-500'
                        }`}
                        style={{
                          width: `${(count / orgDashboard.total_transactions) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Metrics */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">Risk Metrics</h3>
              <div className="space-y-4">
                <div className="p-3 bg-blue-50 rounded">
                  <div className="text-gray-600 text-sm">Organization Risk Score</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {orgDashboard.risk_metrics.org_risk_score}/100
                  </div>
                </div>
                <div className="p-3 bg-teal-50 rounded">
                  <div className="text-gray-600 text-sm">Avg Completion Time</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {orgDashboard.risk_metrics.avg_completion_days.toFixed(1)} days
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Top 3 Risky Users */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">⚠️ Top 3 Risky Users</h3>
              <div className="space-y-3">
                {orgDashboard.top_3_risky_users.length > 0 ? (
                  orgDashboard.top_3_risky_users.map((user, idx) => (
                    <div key={user.user_id} className="p-3 bg-red-50 rounded border-l-4 border-red-500">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-semibold text-gray-900">#{idx + 1} {user.name}</div>
                          <div className="text-sm text-gray-600">{user.email}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            Completed: {user.completed} | Disputed: {user.disputed}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`text-lg font-bold ${
                            user.risk_score > 50 ? 'text-red-600' : 'text-orange-600'
                          }`}>
                            {user.risk_score}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-3">No risky users</p>
                )}
              </div>
            </div>

            {/* Top 3 High Volume Users */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">💰 Top 3 High Volume Users</h3>
              <div className="space-y-3">
                {orgDashboard.top_3_high_volume_users.length > 0 ? (
                  orgDashboard.top_3_high_volume_users.map((user, idx) => (
                    <div key={user.user_id} className="p-3 bg-green-50 rounded border-l-4 border-green-500">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-semibold text-gray-900">#{idx + 1} {user.name}</div>
                          <div className="text-sm text-gray-600">{user.email}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            Bought: ${(user.total_bought / 1000).toFixed(1)}K | Sold: ${(user.total_sold / 1000).toFixed(1)}K
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-green-600">
                            ${(user.total_amount / 1000).toFixed(1)}K
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-3">No high volume users</p>
                )}
              </div>
            </div>
          </div>

          {/* Corrupted Documents */}
          {orgDashboard.corrupted_documents.length > 0 && (
            <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg mb-6">
              <h3 className="text-lg font-bold text-red-900 mb-3">🚨 Corrupted Documents</h3>
              <div className="space-y-2">
                {orgDashboard.corrupted_documents.map((doc) => (
                  <div key={doc.doc_id} className="text-sm text-red-800">
                    <span className="font-semibold">Doc #{doc.doc_id}</span> - {doc.doc_number} ({doc.doc_type})
                    - <span className="text-red-600">{doc.status}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* KPI CARDS */}
      {kpis && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
            <div className="text-gray-500 text-sm font-semibold">Documents</div>
            <div className="text-3xl font-bold text-gray-900">
              {kpis.document_kpis.total}
            </div>
            <div className="text-xs text-green-600 mt-1">
              {kpis.document_kpis.verification_rate}% Verified
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-teal-500">
            <div className="text-gray-500 text-sm font-semibold">Transactions</div>
            <div className="text-3xl font-bold text-gray-900">
              {kpis.transaction_kpis.total}
            </div>
            <div className="text-xs text-green-600 mt-1">
              {kpis.transaction_kpis.settlement_rate}% Settled
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-purple-500">
            <div className="text-gray-500 text-sm font-semibold">Volume</div>
            <div className="text-3xl font-bold text-gray-900">
              ${(kpis.transaction_kpis.total_volume / 1000).toFixed(1)}K
            </div>
            <div className="text-xs text-gray-500 mt-1">USD</div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-yellow-500">
            <div className="text-gray-500 text-sm font-semibold">Health</div>
            <div className={`text-3xl font-bold ${kpis.risk_kpis.health_score >= 70 ? "text-green-600" : "text-yellow-600"}`}>
              {kpis.risk_kpis.health_score}%
            </div>
            <div className="text-xs text-gray-500 mt-1">Risk Adjusted</div>
          </div>
        </div>
      )}

      {/* EXPORT BUTTONS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <button
          onClick={handleExportDocumentsCSV}
          disabled={exporting === "documents-csv"}
          className="bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {exporting === "documents-csv" ? "Exporting..." : "📄 Docs CSV"}
        </button>
        <button
          onClick={handleExportDocumentsPDF}
          disabled={exporting === "documents-pdf"}
          className="bg-red-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
        >
          {exporting === "documents-pdf" ? "Exporting..." : "📄 Docs PDF"}
        </button>
        <button
          onClick={handleExportTransactionsCSV}
          disabled={exporting === "transactions-csv"}
          className="bg-teal-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-teal-700 disabled:opacity-50"
        >
          {exporting === "transactions-csv" ? "Exporting..." : "📊 Txns CSV"}
        </button>
        <button
          onClick={handleExportTransactionsPDF}
          disabled={exporting === "transactions-pdf"}
          className="bg-purple-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
        >
          {exporting === "transactions-pdf" ? "Exporting..." : "📊 Txns PDF"}
        </button>
      </div>

      {/* Transaction Timeline */}
      {transactionAnalytics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-bold mb-4">Transaction Status Breakdown</h2>
            <div className="space-y-2">
              {Object.entries(transactionAnalytics.status_breakdown).map(
                ([status, count]) => (
                  <div key={status} className="flex justify-between">
                    <span className="text-gray-700">{status}</span>
                    <span className="font-semibold text-gray-900">{count}</span>
                  </div>
                )
              )}
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-bold mb-4">Risk Distribution</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-green-600 font-semibold">Low</span>
                <span>{transactionAnalytics.risk_distribution.LOW}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-yellow-600 font-semibold">Medium</span>
                <span>{transactionAnalytics.risk_distribution.MEDIUM}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-orange-600 font-semibold">High</span>
                <span>{transactionAnalytics.risk_distribution.HIGH}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-red-600 font-semibold">Critical</span>
                <span>{transactionAnalytics.risk_distribution.CRITICAL}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {activityLog && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-bold mb-4">Recent Activity (Last 30 days)</h2>
          <div className="space-y-2">
            {activityLog.activities.length > 0 ? (
              activityLog.activities.slice(0, 10).map((activity) => (
                <div
                  key={activity.id}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded"
                >
                  <div>
                    <div className="font-semibold text-gray-900">
                      {activity.action}
                    </div>
                    <div className="text-sm text-gray-500">
                      Document #{activity.document_id} • User #{activity.actor_id}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(activity.timestamp).toLocaleString()}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">No activity yet</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

