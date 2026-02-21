import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getLedgerForDocument } from "../api/ledger";
import { takeAction, getDocumentById } from "../api/documents";
import { getCurrentUser } from "../api/auth";
import { getAllowedActions } from "../utils/permissions";

export default function LedgerExplorer() {
  const { id } = useParams();

  const [ledger, setLedger] = useState<any[]>([]);
  const [user, setUser] = useState<any>(null);
  const [docType, setDocType] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id) return;

    // 🔹 fetch ledger
    getLedgerForDocument(id).then(setLedger);

    // 🔹 fetch document
    getDocumentById(Number(id)).then((doc) => {
      setDocType(doc.doc_type);
    });

    // 🔹 fetch user
    getCurrentUser().then(setUser);
  }, [id]);

  const lastAction =
    ledger.length > 0 ? ledger[ledger.length - 1].action : "ISSUED";

  const allowedActions =
    user && docType
      ? getAllowedActions(docType, lastAction, user.role)
      : [];

  const handleAction = async (action: string) => {
    if (!id) return;

    setLoading(true);
    try {
      await takeAction(Number(id), action);
      const updated = await getLedgerForDocument(id);
      setLedger(updated);
    } catch {
      alert("Action failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-2">Ledger Timeline</h1>

      <div className="text-sm text-gray-500 mb-4">
        Role: {user?.role} | Doc Type: {docType} | Last Action: {lastAction}
      </div>

      {/* ACTION BUTTONS */}
      <div className="mb-6 space-x-3">
        {allowedActions.map((action) => (
          <button
            key={action}
            disabled={loading}
            onClick={() => handleAction(action)}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            {action}
          </button>
        ))}

        {allowedActions.length === 0 && (
          <p className="text-gray-400">No actions available</p>
        )}
      </div>

      {/* LEDGER LIST */}
      <ul className="space-y-3">
        {ledger.map((l, i) => (
          <li key={i} className="border p-3 rounded">
            <div><b>Action:</b> {l.action}</div>
            <div><b>Actor ID:</b> {l.actor_id}</div>
            <div className="text-sm text-gray-500">
              {new Date(l.created_at).toLocaleString()}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}