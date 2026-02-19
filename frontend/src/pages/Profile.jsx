import { useEffect, useState } from "react";
import api from "../services/api";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [risk, setRisk] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    const userId = localStorage.getItem("user_id");

    api.get("/user", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => setUser(res.data))
      .catch(() => alert("Unauthorized"));

    api.get(`/dashboard/risk-score?user_id=${userId}`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setRisk(res.data));
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

  // const riskTone =
  //   risk?.risk_percent >= 50
  //     ? "from-red-500 to-red-600"
  //     : risk?.risk_percent >= 20
  //     ? "from-orange-400 to-orange-500"
  //     : "from-emerald-400 to-emerald-500";

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

// function ActionButton({ label, color, href }) {
//   const map = {
//     blue: "bg-blue-600 hover:bg-blue-700",
//     indigo: "bg-indigo-600 hover:bg-indigo-700",
//     emerald: "bg-emerald-600 hover:bg-emerald-700",
//     slate: "bg-slate-800 hover:bg-slate-900",
//   };

//   return (
//     <a href={href}>
//       <button
//         className={`w-full py-2 rounded-lg text-white font-medium transition shadow ${map[color]}`}
//       >
//         {label}
//       </button>
//     </a>
//   );
// }

