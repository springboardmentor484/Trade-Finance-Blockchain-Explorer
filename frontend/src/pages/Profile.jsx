import { useEffect, useState } from "react";
import api from "../services/api";

export default function Profile() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    api.get("/user", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => setUser(res.data))
      .catch(() => alert("Unauthorized"));
  }, []);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-gray-600 animate-pulse">Loading profile...</div>
      </div>
    );
  }

  const photoUrl = user.photo_url
    ? `${process.env.REACT_APP_API_URL || "http://localhost:8000"}/${user.photo_url}`
    : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 px-4 py-12 flex justify-center">
      <div className="w-full max-w-3xl space-y-8">

        {/* Header Card */}
        <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-2xl p-6 shadow-xl flex items-center gap-5">
          {photoUrl ? (
            <img
              src={photoUrl}
              alt="Profile"
              className="h-20 w-20 rounded-full object-cover border-4 border-white shadow"
              onError={(e) => { e.currentTarget.src = "/avatar.png"; }}
            />
          ) : (
            <div className="h-20 w-20 rounded-full bg-blue-600 text-white flex items-center justify-center text-3xl font-bold shadow">
              {user.name?.[0]?.toUpperCase()}
            </div>
          )}

          <div>
            <h2 className="text-2xl font-bold text-white">{user.name}</h2>
            <p className="text-sm text-slate-300">{user.email}</p>
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <InfoCard title="Role" value={user.role} color="blue" />
          <InfoCard title="Organization" value={user.org} color="indigo" />
          <InfoCard title="Status" value="Active" color="emerald" />
        </div>

      </div>
    </div>
  );
}

function InfoCard({ title, value, color }) {
  const map = {
    blue: "border-blue-500 text-blue-600",
    indigo: "border-indigo-500 text-indigo-600",
    emerald: "border-emerald-500 text-emerald-600",
  };

  return (
    <div className={`bg-white p-5 rounded-xl shadow border-l-4 ${map[color]}`}>
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-lg font-semibold capitalize">{value}</p>
    </div>
  );
}
