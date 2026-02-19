import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import { fetchTransactions, fetchRiskSummary } from "../api/transactions";
import { apiFetch } from "../api";

export default function Dashboard() {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [riskSummary, setRiskSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);
  const [userRole, setUserRole] = useState("admin");

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      
      // Fetch user profile
      const userResponse = await apiFetch("/users/");
      const userData = await userResponse.json();
      if (userResponse.ok) {
        const role = userData.role.toLowerCase();
        setUserInfo(userData);
        setUserRole(role);
        localStorage.setItem("user_role", role);
      }
      
      // Fetch transactions and risk summary
      const [txns, risk] = await Promise.all([
        fetchTransactions(),
        fetchRiskSummary(),
      ]);
      setTransactions(txns);
      setRiskSummary(risk);
    } catch (err) {
      console.error("Error loading dashboard:", err);
    } finally {
      setLoading(false);
    }
  }

  // Prepare data for status distribution pie chart
  const statusData = riskSummary
    ? [
        { name: "Pending", value: riskSummary.pending || 0, color: "#FCD34D" },
        {
          name: "In Progress",
          value: riskSummary.in_progress || 0,
          color: "#60A5FA",
        },
        {
          name: "Completed",
          value: riskSummary.completed || 0,
          color: "#34D399",
        },
        { name: "Disputed", value: riskSummary.disputed || 0, color: "#F87171" },
      ]
    : [];

  // Prepare data for risk distribution
  const riskData = [
    {
      name: "Low",
      count: riskSummary
        ? transactions.filter((t) => t.risk_score < 20).length
        : 0,
      color: "#34D399",
    },
    {
      name: "Medium",
      count: riskSummary
        ? transactions.filter((t) => t.risk_score >= 20 && t.risk_score < 40)
            .length
        : 0,
      color: "#FCD34D",
    },
    {
      name: "High",
      count: riskSummary
        ? transactions.filter((t) => t.risk_score >= 40 && t.risk_score < 60)
            .length
        : 0,
      color: "#FB923C",
    },
    {
      name: "Critical",
      count: riskSummary
        ? transactions.filter((t) => t.risk_score >= 60).length
        : 0,
      color: "#F87171",
    },
  ];

  // Monthly transaction volume
  const monthlyData = [
    { month: "Jan", volume: 45000, count: 12 },
    { month: "Feb", volume: 52000, count: 15 },
    { month: "Mar", volume: 48000, count: 14 },
    { month: "Apr", volume: 61000, count: 18 },
    { month: "May", volume: 55000, count: 16 },
    { month: "Jun", volume: 67000, count: 20 },
  ];

  const roleConfig = {
    admin: {
      title: "⚙️ Admin Dashboard",
      subtitle: "System Overview & Management",
      color: "from-purple-600 to-indigo-600",
    },
    buyer: {
      title: "🛍️ Buyer Dashboard",
      subtitle: "Your Purchase Orders & Transactions",
      color: "from-blue-600 to-cyan-600",
    },
    seller: {
      title: "📦 Seller Dashboard",
      subtitle: "Your Sales & Shipments",
      color: "from-green-600 to-emerald-600",
    },
  };

  const config = roleConfig[userRole] || roleConfig.admin;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className={`bg-gradient-to-r ${config.color} shadow-lg`}>
        <div className="max-w-7xl mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold text-white mb-2">{config.title}</h1>
          <p className="text-blue-100">{config.subtitle}</p>
          {userInfo && (
            <div className="mt-4 text-blue-100 text-sm">
              Logged in as: <span className="font-semibold">{userInfo.name}</span> ({userRole.toUpperCase()})
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center space-x-8">
          <button
            onClick={() => navigate("/transactions")}
            className="px-4 py-2 rounded-lg hover:bg-gray-100 font-semibold text-gray-700 transition"
          >
            📊 Transactions
          </button>
          <button
            onClick={() => navigate("/documents")}
            className="px-4 py-2 rounded-lg hover:bg-gray-100 font-semibold text-gray-700 transition"
          >
            📄 Documents
          </button>
          <button
            onClick={() => {
              localStorage.removeItem("access_token");
              localStorage.removeItem("user_role");
              navigate("/login");
            }}
            className="px-4 py-2 rounded-lg hover:bg-gray-100 font-semibold text-gray-700 transition ml-auto"
          >
            🚪 Logout
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500 hover:shadow-lg transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-semibold">Total Transactions</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {riskSummary?.total_transactions || 0}
                </p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500 hover:shadow-lg transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-semibold">Total Volume</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  ₹{((riskSummary?.total_volume || 0) / 1000000).toFixed(1)}M
                </p>
              </div>
              <div className="text-4xl">💰</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500 hover:shadow-lg transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-semibold">Average Risk</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {(riskSummary?.average_risk_score || 0).toFixed(0)}/100
                </p>
              </div>
              <div className="text-4xl">⚠️</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500 hover:shadow-lg transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-semibold">High Risk</p>
                <p className="text-3xl font-bold text-red-600 mt-2">
                  {riskSummary?.high_risk_count || 0}
                </p>
              </div>
              <div className="text-4xl">🔴</div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          {/* Status Distribution */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Transaction Status</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Risk Distribution */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Risk Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={riskData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8" radius={[8, 8, 0, 0]}>
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Performance */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Monthly Transaction Volume</h3>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={monthlyData}>
              <defs>
                <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="volume"
                stroke="#3B82F6"
                fillOpacity={1}
                fill="url(#colorVolume)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-gray-900">Recent Transactions</h3>
            <button
              onClick={() => navigate("/transactions")}
              className="text-blue-600 hover:text-blue-800 font-semibold text-sm"
            >
              View All →
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">ID</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Buyer</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Seller</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Amount</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Risk</th>
                </tr>
              </thead>
              <tbody>
                {transactions.slice(0, 5).map((tx) => (
                  <tr key={tx.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 font-bold text-gray-900">#{tx.id}</td>
                    <td className="px-6 py-4 text-gray-700">{tx.buyer_id}</td>
                    <td className="px-6 py-4 text-gray-700">{tx.seller_id}</td>
                    <td className="px-6 py-4 font-semibold text-gray-900">
                      ₹{tx.amount.toLocaleString("en-IN")}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          tx.status === "COMPLETED"
                            ? "bg-green-100 text-green-800"
                            : tx.status === "PENDING"
                            ? "bg-yellow-100 text-yellow-800"
                            : tx.status === "IN_PROGRESS"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {tx.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          tx.risk_score < 20
                            ? "bg-green-100 text-green-800"
                            : tx.risk_score < 40
                            ? "bg-yellow-100 text-yellow-800"
                            : tx.risk_score < 60
                            ? "bg-orange-100 text-orange-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {tx.risk_score.toFixed(0)} pts
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
