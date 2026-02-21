export default function LedgerTimeline({ ledger }) {
  const getActionIcon = (action) => {
    const icons = {
      ISSUED: "📄",
      ACCEPTED: "✅",
      SHIPPED: "🚚",
      RECEIVED: "📦",
      VERIFIED: "🔒",
      PAID: "💰",
    };
    return icons[action] || "•";
  };

  const getEntryStyle = (action) => {
    if (action === "VERIFIED") {
      return "border-green-300 bg-green-50 dark:bg-green-900/20";
    }
    if (action === "PAID") {
      return "border-blue-300 bg-blue-50 dark:bg-blue-900/20";
    }
    return "border-gray-300 bg-white";
  };

  return (
    <div className="space-y-3">
      {ledger && ledger.length > 0 ? (
        ledger.map((entry) => (
          <div
            key={entry.id}
            className={`p-4 border rounded-md ${getEntryStyle(entry.action)}`}
          >
            <div className="flex justify-between items-start">
              <div className="flex gap-3">
                <span className="text-lg">{getActionIcon(entry.action)}</span>
                <div>
                  <div className="font-bold text-gray-900 dark:text-white">
                    {entry.action}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Actor ID: {entry.actor_id}
                  </div>
                </div>
              </div>
              <div className="text-xs text-gray-500">
                {new Date(entry.timestamp || entry.created_at).toLocaleString()}
              </div>
            </div>
            {entry.meta && Object.keys(entry.meta).length > 0 && (
              <div className="mt-3 pl-8 text-sm text-gray-700 dark:text-gray-300">
                {Object.entries(entry.meta).map(([key, value]) => (
                  <div key={key} className="break-all">
                    <span className="font-semibold">{key}:</span>{" "}
                    {typeof value === "string" && value.length > 50
                      ? value.substring(0, 47) + "..."
                      : String(value)}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))
      ) : (
        <div className="text-gray-500 text-center py-4">No ledger entries yet</div>
      )}
    </div>
  );
}
