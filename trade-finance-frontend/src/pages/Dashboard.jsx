import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, PieChart, Pie, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts/es6';
import { TrendingUp, AlertTriangle, DollarSign, Package } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [riskSummary, setRiskSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const [statsRes, riskRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/transactions/stats/summary`),
        axios.get(`${API_BASE_URL}/risk/summary`)
      ]);

      setStats(statsRes.data);
      setRiskSummary(riskRes.data);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-600">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-700 rounded">
        {error}
      </div>
    );
  }

  // Prepare chart data
  const statusData = stats && stats.by_status ? [
    { name: 'Pending', value: stats.by_status.pending || 0 },
    { name: 'In Progress', value: stats.by_status.in_progress || 0 },
    { name: 'Completed', value: stats.by_status.completed || 0 },
    { name: 'Disputed', value: stats.by_status.disputed || 0 }
  ] : [];

  const currencyData = stats && stats.by_currency ? Object.entries(stats.by_currency).map(([curr, amount]) => ({
    currency: curr,
    amount: amount
  })) : [];

  const riskData = riskSummary ? [
    { name: 'Low Risk', value: riskSummary.low_risk_count },
    { name: 'Medium Risk', value: riskSummary.medium_risk_count },
    { name: 'High Risk', value: riskSummary.high_risk_count }
  ] : [];

  const avgCompletionTime = stats && stats.average_completion_time_seconds
    ? (stats.average_completion_time_seconds / 86400).toFixed(2)
    : 0;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        {/* KPI Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Transactions</p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats?.total_transactions || 0}
                </p>
              </div>
              <Package className="text-blue-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Amount</p>
                <p className="text-3xl font-bold text-gray-900">
                  ${(stats?.total_amount || 0).toLocaleString('en-US', {
                    maximumFractionDigits: 0
                  })}
                </p>
              </div>
              <DollarSign className="text-green-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Avg Risk Score</p>
                <p className="text-3xl font-bold text-gray-900">
                  {(riskSummary?.average_risk_score || 0).toFixed(1)}%
                </p>
              </div>
              <AlertTriangle className="text-orange-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Avg Completion</p>
                <p className="text-3xl font-bold text-gray-900">
                  {avgCompletionTime} days
                </p>
              </div>
              <TrendingUp className="text-purple-600" size={32} />
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          {/* Transaction Status Pie Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Transactions by Status
            </h2>
            {statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">No data available</p>
            )}
          </div>

          {/* Risk Distribution Pie Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Risk Distribution
            </h2>
            {riskData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    <Cell fill="#10b981" />
                    <Cell fill="#f59e0b" />
                    <Cell fill="#ef4444" />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">No data available</p>
            )}
          </div>
        </div>

        {/* Currency Distribution Bar Chart */}
        {currencyData.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Transaction Amount by Currency
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={currencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="currency" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Legend />
                <Bar dataKey="amount" fill="#3b82f6" name="Amount" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Top Risky Users */}
        {riskSummary && riskSummary.top_risky_users && riskSummary.top_risky_users.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Top Risky Users
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-4 font-semibold">User</th>
                    <th className="text-left py-2 px-4 font-semibold">Email</th>
                    <th className="text-left py-2 px-4 font-semibold">Risk Score</th>
                    <th className="text-left py-2 px-4 font-semibold">Disputes</th>
                    <th className="text-left py-2 px-4 font-semibold">Rationale</th>
                  </tr>
                </thead>
                <tbody>
                  {riskSummary.top_risky_users.map((user) => (
                    <tr key={user.user_id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">{user.user_name}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{user.email}</td>
                      <td className="py-3 px-4">
                        <span className={`font-bold ${
                          user.risk_score >= 30 ? 'text-red-600' :
                          user.risk_score >= 10 ? 'text-orange-600' :
                          'text-green-600'
                        }`}>
                          {user.risk_score.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3 px-4">{user.disputed_count} / {user.total_count}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{user.rationale}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
