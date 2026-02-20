import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

export default function DocumentDetail() {
  const { id } = useParams();
  const [doc, setDoc] = useState(null);
  const [hashResult, setHashResult] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    api
      .get(`/document?id=${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setDoc(res.data))
      .catch(() => alert("Access Denied"));
  }, [id]);

  if (!doc) return <div className="p-10 text-center text-gray-500">Loading document...</div>;

  const role = localStorage.getItem("role");
  const status = doc.document.status;
  const docType = doc.document.doc_type;

  const performAction = (action) => {
    const token = localStorage.getItem("accessToken");

    api
      .post("/action", null, {
        params: { doc_id: id, action },
        headers: { Authorization: `Bearer ${token}` },
      })
      .then(() => window.location.reload())
      .catch(() => alert("Action not allowed"));
  };

  const verifyHash = () => {
    const token = localStorage.getItem("accessToken");

    api
      .get(`/verify-hash?document_id=${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setHashResult(res.data))
      .catch(() => alert("Hash verification failed"));
  };

  const disableVerify = hashResult?.is_valid || doc.document.is_compromised;

  const docIcon = (type) => {
    if (type === "PO") return "📝";
    if (type === "BOL") return "📦";
    if (type === "INVOICE") return "🧾";
    if (type === "LOC") return "🏦";
    return "📄";
  };

  const statusStyles = {
    CREATED: "border-l-gray-400 bg-gray-50 text-gray-700",
    ISSUE_BOL: "border-l-orange-500 bg-orange-50 text-orange-700",
    SHIP: "border-l-blue-500 bg-blue-50 text-blue-700",
    RECEIVE: "border-l-green-500 bg-green-50 text-green-700",
    VERIFY: "border-l-purple-500 bg-purple-50 text-purple-700",
    ISSUE_LOC: "border-l-indigo-500 bg-indigo-50 text-indigo-700",
    PAY: "border-l-emerald-500 bg-emerald-50 text-emerald-700",
  };

  const actionDot = (action) => {
    if (action === "ISSUE_BOL") return "bg-orange-500";
    if (action === "SHIP") return "bg-blue-500";
    if (action === "RECEIVE") return "bg-green-500";
    if (action === "VERIFY") return "bg-purple-500";
    if (action === "ISSUE_LOC") return "bg-indigo-500";
    if (action === "PAY") return "bg-emerald-500";
    return "bg-gray-400";
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className={`max-w-5xl mx-auto bg-white rounded-2xl shadow p-6 space-y-8 border-l-4 ${statusStyles[status] || "border-l-gray-400"}`}>

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{docIcon(docType)}</span>
            <div>
              <h2 className="text-2xl font-bold">
                {doc.document.doc_number}
              </h2>
              <p className="text-sm text-gray-500">
                {docType} Document
              </p>
            </div>
          </div>

          <span className="px-3 py-1 rounded-full text-sm font-semibold bg-white border shadow-sm">
            {status}
          </span>
        </div>

        {/* Compromised Warning */}
        {doc.document.is_compromised && (
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-800">
            ⚠️ <strong>Integrity Alert:</strong> This document failed hash verification.
          </div>
        )}

        {/* Role Actions */}
        <Section title="⚙️ Available Actions">
          <div className="flex flex-wrap gap-2">
            {role === "seller" && docType === "PO" && status === "CREATED" && (
              <ActionBtn color="orange" onClick={() => performAction("ISSUE_BOL")}>
                Issue BOL
              </ActionBtn>
            )}

            {role === "seller" && status === "ISSUE_BOL" && (
              <ActionBtn color="blue" onClick={() => performAction("SHIP")}>
                Ship
              </ActionBtn>
            )}

            {role === "buyer" && status === "SHIP" && (
              <ActionBtn color="green" onClick={() => performAction("RECEIVE")}>
                Receive
              </ActionBtn>
            )}

            {role === "auditor" && status !== "VERIFY" && (
              <ActionBtn color="purple" onClick={() => performAction("VERIFY")}>
                Verify
              </ActionBtn>
            )}

            {role === "bank" && status === "CREATED" && (
              <ActionBtn color="indigo" onClick={() => performAction("ISSUE_LOC")}>
                Issue LOC
              </ActionBtn>
            )}

            {role === "bank" && status === "RECEIVE" && (
              <ActionBtn color="emerald" onClick={() => performAction("PAY")}>
                Pay
              </ActionBtn>
            )}

            {role === "auditor" && status !== "VERIFY" && (
              <button
                onClick={() => performAction("VERIFY")}
                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition shadow"
              >
                🔍 Verify Document
              </button>
            )}

          </div>
        </Section>

        {/* File Actions */}
        <Section title="📂 File Actions">
          <div className="flex flex-wrap gap-3">
            <a
              href={`http://127.0.0.1:8000/file?file_url=${doc.document.file_url}`}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 bg-sky-500 text-white rounded-lg hover:bg-sky-600 shadow"
            >
              Download File
            </a>

            <button
              onClick={verifyHash}
              disabled={disableVerify}
              className={`px-4 py-2 rounded-lg text-white shadow ${
                disableVerify
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-green-600 hover:bg-green-700"
              }`}
            >
              Verify Integrity
            </button>
          </div>

          {hashResult && (
            <div className="mt-4 p-4 rounded-lg border bg-slate-50">
              <p className="text-sm text-gray-600 mb-2">🔗 Blockchain Hash Comparison</p>

              <div className="space-y-2 text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="w-32 text-gray-500">Stored Hash:</span>
                  <span className="truncate">{hashResult.stored_hash}</span>
                </div>

                <div className="flex items-center gap-2 animate-pulse">
                  <span className="w-32 text-gray-500">Current Hash:</span>
                  <span className="truncate">{hashResult.current_hash}</span>
                </div>
              </div>

              {hashResult.is_valid ? (
                <p className="mt-3 text-green-700 font-semibold">✅ Hash matched. Integrity intact.</p>
              ) : (
                <p className="mt-3 text-red-700 font-semibold">❌ Hash mismatch. Document compromised.</p>
              )}
            </div>
          )}

        </Section>

        {/* Ledger Timeline */}
        <Section title="🧾 Ledger Timeline">
          <div className="relative border-l-2 border-gray-300 pl-6 space-y-6">
            {doc.ledger.map((entry, index) => (
              <div key={index} className="relative">
                <span
                  className={`absolute -left-[9px] top-1.5 w-4 h-4 rounded-full ${actionDot(entry.action)}`}
                ></span>

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
                </div>
              </div>
            ))}
          </div>
        </Section>

      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      {children}
    </div>
  );
}

function ActionBtn({ color, children, onClick }) {
  const colors = {
    orange: "bg-orange-500 hover:bg-orange-600",
    blue: "bg-blue-500 hover:bg-blue-600",
    green: "bg-green-500 hover:bg-green-600",
    purple: "bg-purple-500 hover:bg-purple-600",
    indigo: "bg-indigo-500 hover:bg-indigo-600",
    emerald: "bg-emerald-500 hover:bg-emerald-600",
  };

  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg text-white shadow ${colors[color]}`}
    >
      {children}
    </button>
  );
}
