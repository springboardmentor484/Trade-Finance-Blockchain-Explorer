import { useEffect, useState } from "react";
import api from "../services/api";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";

export default function Dashboard() {
  const [totals, setTotals] = useState(null);
  const [breakdown, setBreakdown] = useState(null);
  const [risk, setRisk] = useState(null);
  const [topRisky, setTopRisky] = useState([]);
  const [topVolume, setTopVolume] = useState([]);
  const [corruptedDocs, setCorruptedDocs] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [externalStats, setExternalStats] = useState(null);


  const role = localStorage.getItem("role");
  const org = localStorage.getItem("org");
  const userId = localStorage.getItem("user_id");
  const name = localStorage.getItem("name") || "User";

  useEffect(() => {
  api.get(`/dashboard/org/totals?org_name=${org}`).then(res => setTotals(res.data));
  api.get(`/dashboard/org/status-breakdown?org_name=${org}`).then(res => setBreakdown(res.data.breakdown));
  api.get(`/dashboard/risk-score?user_id=${userId}`).then(res => setRisk(res.data));

  if (role === "bank" || role === "auditor") {
    api.get("/dashboard/top-risky-users").then(res => setTopRisky(res.data));
    api.get("/dashboard/top-volume-users").then(res => setTopVolume(res.data));
    api.get("/alerts/compromised-documents").then(res => setCorruptedDocs(res.data));
  }

  api.get("/dashboard/trend").then(res => setTrendData(res.data));

  api.get("/external/trade-snapshot").then(res => setExternalStats(res.data));

}, [role, org, userId]);


  const exportCsv = async () => {
    const res = await api.get(`/dashboard/org/export?org_name=${org}`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${org}_dashboard.csv`);
    document.body.appendChild(link);
    link.click();
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8 space-y-8">

      {/* Hero */}
      <div className="bg-gradient-to-r from-blue-800 to-indigo-900 text-white rounded-2xl p-8 shadow">
        <h1 className="text-3xl font-bold">Welcome to TradeSecure, {name} 👋</h1>
        <p className="text-blue-100 mt-1">
          Your secure platform for transaction integrity and analytics
        </p>
      </div>

      {/* KPIs */}
      {totals && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <KPI title="Total Bought" value={`₹ ${totals.total_bought}`} color="from-blue-500 to-blue-700" />
          <KPI title="Total Sold" value={`₹ ${totals.total_sold}`} color="from-green-500 to-green-700" />
          <KPI title="Total Amount" value={`₹ ${totals.total_amount}`} color="from-indigo-500 to-indigo-700" />
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {breakdown && (
            <Card title="📌 Transaction Status">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(breakdown).map(([status, count]) => (
                  <div key={status} className="bg-slate-100 rounded-xl p-4 text-center">
                    <p className="text-sm text-gray-500 capitalize">{status}</p>
                    <p className="text-2xl font-bold">{count}</p>
                  </div>
                ))}
              </div>

              {/* ✅ REAL GRAPH (Recharts) */}
              <div className="mt-6 h-56 bg-white rounded-xl p-3">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="completed" stroke="#22c55e" strokeWidth={2} />
                    <Line type="monotone" dataKey="disputed" stroke="#ef4444" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}

          {(role === "bank" || role === "auditor") && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Leaderboard title="🔴 Top 3 Risky Users" rows={topRisky} type="risk" />
              <Leaderboard title="🟢 Top 3 High Volume Users" rows={topVolume} type="volume" />
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-6">

          {/* Risk Pie */}
          {risk && (
            <Card title="⚠️ User Risk Score">
              <RiskRing percent={risk.risk_percent} />
              <div className="mt-3 text-center text-sm text-gray-600">
                Completed: {risk.completed} | Disputed: {risk.disputed}
              </div>
            </Card>
          )}

          <Card title="🚨 Corrupted Documents">
            {corruptedDocs.length === 0 ? (
              <p className="text-gray-500">No corrupted documents 🎉</p>
            ) : (
              corruptedDocs.map((d, i) => (
                <div key={i} className="p-3 bg-red-50 border-l-4 border-red-600 rounded mb-2">
                  <p className="font-medium text-red-700">
                    🚨 Doc #{d.id} ({d.doc_type})
                  </p>
                  <p className="text-xs text-gray-600">
                    Owner: {d.owner_id} · Status: {d.status}
                  </p>
                </div>

              ))
            )}
          </Card>

          {externalStats && (
            <Card title="🌍 Global Trade Snapshot (UNCTAD)">
              <div className="space-y-2 text-sm text-gray-700">
                <p>
                  <span className="font-medium">Country:</span> {externalStats.country} ({externalStats.year})
                </p>
                <p>
                  <span className="font-medium">Imports:</span> ${externalStats.imports_usd_billion}B
                </p>
                <p>
                  <span className="font-medium">Exports:</span> ${externalStats.exports_usd_billion}B
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  Source: {externalStats.source} · {externalStats.note}
                </p>
              </div>
            </Card>
          
        
)}


          <button
            onClick={exportCsv}
            className="w-full py-3 bg-blue-600 text-white rounded-xl shadow hover:bg-blue-700"
          >
            Export Dashboard CSV
          </button>
        </div>
      </div>
    </div>
  );
}

/* ---------- UI Components ---------- */

function KPI({ title, value, color }) {
  return (
    <div className={`bg-gradient-to-r ${color} text-white p-6 rounded-2xl shadow`}>
      <p className="text-sm opacity-90">{title}</p>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      {children}
    </div>
  );
}

function Leaderboard({ title, rows, type }) {
  return (
    <Card title={title}>
      <div className="space-y-3">
        {rows.map((u) => (
          <div
            key={u.user_id}
            className="flex items-center justify-between bg-slate-50 p-3 rounded-lg hover:shadow transition"
          >
            <div className="flex items-center gap-3">
              <img
                src={u.avatar_url || `https://api.dicebear.com/7.x/initials/svg?seed=${u.name}`}
                alt="avatar"
                className="w-10 h-10 rounded-full object-cover border"
              />
              <div>
                <p className="font-medium">{u.name}</p>
                <p className="text-xs text-gray-500">{u.org}</p>
              </div>
            </div>
            <p className={`font-semibold ${type === "risk" ? "text-red-600" : "text-green-600"}`}>
              {type === "risk" ? `${u.risk_percent}%` : `₹ ${u.total_amount}`}
            </p>
          </div>
        ))}
      </div>
    </Card>
  );
}

function RiskRing({ percent }) {
  return (
    <div className="relative w-32 h-32 mx-auto">
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: `conic-gradient(#22c55e ${100 - percent}%, #ef4444 0 ${percent}%, #e5e7eb 0)`
        }}
      />
      <div className="absolute inset-3 bg-white rounded-full flex items-center justify-center">
        <span className="text-2xl font-bold">{percent}%</span>
      </div>
    </div>
  );
}
