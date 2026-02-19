import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  fetchTransaction,
  executeTransactionStep,
  markDisputed
} from "../api/transactions";

export default function TransactionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("details");
  const [processing, setProcessing] = useState(false);

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

  /* =====================================================
     🔥 NEW UNIFIED STEP HANDLER
  ===================================================== */
  async function handleStep(stepName, payload = null) {
    try {
      setProcessing(true);
      await executeTransactionStep(id, stepName, payload);
      await loadTransaction();
    } catch (err) {
      alert(err.message);
    } finally {
      setProcessing(false);
    }
  }

  async function handleDispute() {
    const reason = prompt("Enter dispute reason:");
    if (!reason) return;

    try {
      setProcessing(true);
      await markDisputed(id, reason);
      await loadTransaction();
    } catch (err) {
      alert(err.message);
    } finally {
      setProcessing(false);
    }
  }

  if (loading) return <div className="p-6">Loading transaction...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error}</div>;
  if (!transaction) return <div className="p-6">Transaction not found</div>;

  /* ===============================
     🔥 SAFE RISK SCORE FIX
     Prevent crash if undefined
  ================================*/
  const safeRiskScore = Number(transaction.risk_score || 0);

  const statusColor = {
    PENDING: "bg-yellow-100 text-yellow-800 border-yellow-300",
    IN_PROGRESS: "bg-blue-100 text-blue-800 border-blue-300",
    COMPLETED: "bg-green-100 text-green-800 border-green-300",
    DISPUTED: "bg-red-100 text-red-800 border-red-300",
    CANCELLED: "bg-gray-100 text-gray-800 border-gray-300",
  };

  const statusBg =
    statusColor[transaction.status] || "bg-gray-100 text-gray-800";

  return (
    <div className="min-h-screen bg-gray-50">
      {/* HEADER */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Trade Transactions
              </h1>
              <p className="text-gray-600 mt-1">Transaction ID: {id}</p>
            </div>
            <button
              onClick={() => navigate("/transactions")}
              className="text-blue-600 hover:text-blue-800 font-semibold"
            >
              ← Back to List
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* MAIN CARD */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="flex justify-between items-start mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Transaction Information
            </h2>
            <div
              className={`px-4 py-2 rounded-lg border font-semibold text-lg ${statusBg}`}
            >
              {transaction.status}
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
            <Info label="Transaction ID" value={transaction.id} />
            <Info label="Buyer ID" value={transaction.buyer_id} />
            <Info label="Seller ID" value={transaction.seller_id} />

            <Info
              label="Amount"
              value={`₹ ${transaction.amount.toLocaleString("en-IN", {
                minimumFractionDigits: 2,
              })}`}
            />

            <Info label="Currency" value={transaction.currency} />

            {/* 🔥 SAFE RISK DISPLAY */}
            <Info
              label="Risk Score"
              value={`${safeRiskScore.toFixed(1)}/100`}
            />

            <Info
              label="Created At"
              value={new Date(transaction.created_at).toLocaleString()}
            />

            <Info
              label="Updated At"
              value={new Date(transaction.updated_at).toLocaleString()}
            />

            <div className="col-span-3">
              <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
                Description
              </label>
              <p className="text-gray-900 text-lg mt-1">
                {transaction.description}
              </p>
            </div>
          </div>
        </div>

        {/* 🔥 ACTION PANEL */}
        <div className="bg-white rounded-lg shadow-md p-8 mt-6">
          <h3 className="text-xl font-bold mb-6 text-gray-900">
            ⚙ Transaction Workflow
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <ActionButton
              label="Create PO"
              onClick={() => handleStep("create-po")}
              disabled={processing}
            />

            <ActionButton
              label="Issue LOC"
              onClick={() => handleStep("issue-loc")}
              disabled={processing}
            />

            <ActionButton
              label="Verify"
              onClick={() => handleStep("verify")}
              disabled={processing}
            />

            <ActionButton
              label="Mark Completed"
              onClick={() => handleStep("mark-completed")}
              disabled={processing}
            />

            <button
              onClick={handleDispute}
              disabled={processing}
              className="bg-red-500 hover:bg-red-600 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
            >
              Mark Disputed
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ===============================
   REUSABLE UI COMPONENTS
=================================*/

function Info({ label, value }) {
  return (
    <div>
      <label className="text-gray-600 text-sm font-semibold uppercase tracking-wide">
        {label}
      </label>
      <p className="text-gray-900 text-lg font-bold mt-1">{value}</p>
    </div>
  );
}

function ActionButton({ label, onClick, disabled }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
    >
      {label}
    </button>
  );
}
