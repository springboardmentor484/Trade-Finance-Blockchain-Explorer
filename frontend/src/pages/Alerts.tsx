import { useEffect, useState } from "react";
import { getAlerts } from "../api/alerts";

interface Alert {
  id: number;
  document_id: number;
  message: string;
  created_at: string;
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    const fetchAlerts = async () => {
      const data = await getAlerts();
      setAlerts(data);
    };

    fetchAlerts();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Integrity Alerts</h1>

      <table className="w-full border">
        <thead>
          <tr className="bg-red-200">
            <th>ID</th>
            <th>Document ID</th>
            <th>Message</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.id} className="text-center border-t">
              <td>{alert.id}</td>
              <td>{alert.document_id}</td>
              <td className="text-red-600">{alert.message}</td>
              <td>{alert.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}