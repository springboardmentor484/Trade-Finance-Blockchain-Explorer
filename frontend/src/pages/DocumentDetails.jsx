import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  fetchDocumentRead,
  performDocumentAction,
  verifyDocument,
  downloadFile,
} from "../api/documents";
import ActionButtons from "../components/ActionButtons";
import StatusBadge from "../components/StatusBadge";
import LedgerTimeline from "../components/LedgerTimeline";

export default function DocumentDetails() {
  const { id: docId } = useParams();
  const navigate = useNavigate();
  const [document, setDocument] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [allowedActions, setAllowedActions] = useState([]);
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);

  useEffect(() => {
    loadDocument();
  }, [docId]);

  async function loadDocument() {
    try {
      setLoading(true);
      const res = await fetchDocumentRead(docId);
      setDocument(res);
      setAllowedActions(res.allowed_actions || []);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAction(action) {
    try {
      await performDocumentAction(docId, action);
      await loadDocument();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleVerify() {
    setVerifying(true);
    setError("");
    try {
      const result = await verifyDocument(docId);
      setVerificationResult(result);
      await loadDocument(); // Refresh to show new ledger entry
    } catch (err) {
      setError(err.message);
    } finally {
      setVerifying(false);
    }
  }

  async function handleDownload() {
    try {
      const blob = await downloadFile(docId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = document.document.file_url || "document";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <div className="p-6">Loading...</div>;
  if (error && !document)
    return (
      <div className="p-6 text-red-500">
        Error: {error}
        <button
          className="ml-4 bg-teal-600 text-white px-4 py-2 rounded"
          onClick={loadDocument}
        >
          Retry
        </button>
      </div>
    );
  if (!document) return <div className="p-6">Document not found</div>;

  const { document: doc, ledger } = document;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>
      )}

      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <button
            onClick={() => navigate("/documents")}
            className="text-teal-600 hover:underline mb-2"
          >
            ← Back to Documents
          </button>
          <h1 className="text-3xl font-bold">{doc.doc_number}</h1>
          <p className="text-gray-600 mt-1">{doc.doc_type}</p>
        </div>
        <StatusBadge status={doc.status} />
      </div>

      {/* Verification Section */}
      <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-6">
        <h3 className="font-bold mb-3">Document Integrity</h3>
        <button
          onClick={handleVerify}
          disabled={verifying}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 mr-3"
        >
          {verifying ? "Verifying..." : "🔒 Verify Integrity"}
        </button>
        <button
          onClick={handleDownload}
          className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
        >
          📥 Download File
        </button>

        {verificationResult && (
          <div className={`mt-4 p-3 rounded ${verificationResult.is_valid ? "bg-green-100" : "bg-red-100"}`}>
            <p
              className={`font-bold ${verificationResult.is_valid ? "text-green-700" : "text-red-700"}`}
            >
              {verificationResult.message}
            </p>
            <p className="text-xs text-gray-600 mt-2 font-mono break-all">
              Hash: {verificationResult.computed_hash.substring(0, 16)}...
            </p>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="mb-6">
        <h3 className="font-bold mb-3">Actions</h3>
        <ActionButtons actions={allowedActions} onAction={handleAction} />
      </div>

      {/* Ledger Timeline */}
      <div>
        <h2 className="text-xl font-bold mb-4">Ledger Timeline</h2>
        <LedgerTimeline ledger={ledger} />
      </div>
    </div>
  );
}
