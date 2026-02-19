import React, { useEffect, useState } from "react";

interface RiskScore {
  id: number;
  user_id: number;
  score: number;
  rationale: string;
  last_updated: string;
}

const RiskScores: React.FC = () => {
  const [data, setData] = useState<RiskScore[]>([]);

  useEffect(() => {
    fetch("/api/risk-audit/risk-scores")
      .then(res => res.json())
      .then((json: RiskScore[]) => setData(json))
      .catch(err => console.error("Failed to fetch risk scores:", err));
  }, []);

  const exportCSV = () => {
    const header = ["ID", "User ID", "Score", "Rationale", "Last Updated"];
    const rows = data.map(r => [r.id, r.user_id, r.score, `"${r.rationale}"`, r.last_updated]);
    const csvContent =
      "data:text/csv;charset=utf-8," +
      [header, ...rows].map(e => e.join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "risk_scores.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Risk Scores</h1>
        <button
          onClick={exportCSV}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Export CSV
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="table-auto w-full border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 border">ID</th>
              <th className="px-4 py-2 border">User ID</th>
              <th className="px-4 py-2 border">Score</th>
              <th className="px-4 py-2 border">Rationale</th>
              <th className="px-4 py-2 border">Last Updated</th>
            </tr>
          </thead>
          <tbody>
            {data.map(r => (
              <tr key={r.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 border">{r.id}</td>
                <td className="px-4 py-2 border">{r.user_id}</td>
                <td className="px-4 py-2 border">{r.score}</td>
                <td className="px-4 py-2 border">{r.rationale}</td>
                <td className="px-4 py-2 border">
                  {new Date(r.last_updated).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RiskScores;