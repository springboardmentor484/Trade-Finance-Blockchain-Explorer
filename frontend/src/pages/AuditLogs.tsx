import React, { useEffect, useState } from "react";

interface AuditLog {
  id: number;
  admin_id: number;
  action: string;
  target_type: string;
  target_id: number | null;
  timestamp: string;
}

const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);

  useEffect(() => {
    fetch("/api/risk-audit/audit-logs")
      .then(res => res.json())
      .then((json: AuditLog[]) => setLogs(json))
      .catch(err => console.error("Failed to fetch audit logs:", err));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Audit Logs</h1>
      <div className="overflow-x-auto">
        <table className="table-auto w-full border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 border">ID</th>
              <th className="px-4 py-2 border">Admin ID</th>
              <th className="px-4 py-2 border">Action</th>
              <th className="px-4 py-2 border">Target Type</th>
              <th className="px-4 py-2 border">Target ID</th>
              <th className="px-4 py-2 border">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 border">{log.id}</td>
                <td className="px-4 py-2 border">{log.admin_id}</td>
                <td className="px-4 py-2 border">{log.action}</td>
                <td className="px-4 py-2 border">{log.target_type}</td>
                <td className="px-4 py-2 border">{log.target_id ?? "-"}</td>
                <td className="px-4 py-2 border">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AuditLogs;