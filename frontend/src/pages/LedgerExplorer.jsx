import { useEffect, useState } from "react";
import { getDocuments } from "../api/client";

export default function LedgerExplorer() {
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    getDocuments(token).then(setDocs).catch(console.error);
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Ledger Explorer</h2>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th>ID</th>
            <th>Doc Number</th>
            <th>Type</th>
            <th>Hash</th>
          </tr>
        </thead>
        <tbody>
          {docs.map(d => (
            <tr key={d.id} className="border-t">
              <td>{d.id}</td>
              <td>{d.doc_number}</td>
              <td>{d.doc_type}</td>
              <td className="text-xs">{d.hash}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}