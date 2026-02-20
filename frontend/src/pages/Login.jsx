import { useState } from "react";
import api from "../services/api";
import logo from "../assets/tradesecure-logo.png";   // ✅ ADD THIS

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [org, setOrg] = useState("");
  const [role, setRole] = useState("buyer");
  const [photo, setPhoto] = useState(null);

  const inputClass =
    "w-full p-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition";

  const login = async () => {
    setError("");
    setLoading(true);

    try {
      const res = await api.post("/login", null, {
        params: { email, password }
      });

      localStorage.setItem("accessToken", res.data.access_token);

      const payload = JSON.parse(atob(res.data.access_token.split(".")[1]));
      localStorage.setItem("role", payload.role);
      localStorage.setItem("user_id", payload.user_id);
      localStorage.setItem("org", payload.org);
      localStorage.setItem("name", payload.name);

      window.location.href = "/dashboard";
    } catch (err) {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  const register = async () => {
    try {
      const formData = new FormData();
      formData.append("name", name);
      formData.append("email", email);
      formData.append("password", password);
      formData.append("role", role);
      formData.append("org_name", org);
      if (photo) formData.append("photo", photo);

      await api.post("/create-user", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      alert("User created. Now login.");
      setIsRegister(false);
      setPhoto(null);
    } catch (err) {
      alert("Registration failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-gray-100">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md animate-fade-in">

        {/* ✅ Logo */}
        <div className="flex justify-center mb-3">
          <img
            src={logo}
            alt="TradeSecure Logo"
            className="h-14 object-contain"
          />
        </div>

        <p className="text-center text-gray-500 mb-6">
          {isRegister ? "Create your account" : "Sign in to continue"}
        </p>

        {error && (
          <div className="mb-4 p-2 text-sm text-red-700 bg-red-100 rounded">
            {error}
          </div>
        )}

        {isRegister && (
          <>
            <div className="mb-3">
              <label className="text-sm text-gray-600">Full Name</label>
              <input
                className={inputClass}
                placeholder="Ashwith D"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div className="mb-3">
              <label className="text-sm text-gray-600">Organization</label>
              <input
                className={inputClass}
                placeholder="ABC Exports Ltd."
                value={org}
                onChange={(e) => setOrg(e.target.value)}
              />
            </div>

            <div className="mb-3">
              <label className="text-sm text-gray-600">Role</label>
              <select
                className={inputClass}
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                <option value="buyer">Buyer</option>
                <option value="seller">Seller</option>
                <option value="bank">Bank</option>
                <option value="auditor">Auditor</option>
              </select>
            </div>

            <div className="mb-4">
              <label className="text-sm text-gray-600">Profile Photo (optional)</label>
              <input
                type="file"
                accept="image/*"
                className="w-full text-sm"
                onChange={(e) => setPhoto(e.target.files[0])}
              />
            </div>
          </>
        )}

        <div className="mb-3">
          <label className="text-sm text-gray-600">Email</label>
          <input
            type="email"
            className={inputClass}
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="mb-6">
          <label className="text-sm text-gray-600">Password</label>
          <input
            type="password"
            className={inputClass}
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button
          onClick={isRegister ? register : login}
          disabled={loading}
          className={`w-full py-2.5 rounded-lg text-white font-medium transition-all duration-200 
            ${loading ? "bg-blue-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700 hover:shadow-md"}
          `}
        >
          {loading ? "Please wait..." : isRegister ? "Create Account" : "Login"}
        </button>

        <div className="text-center mt-5">
          <button
            onClick={() => setIsRegister(!isRegister)}
            className="text-blue-600 text-sm hover:underline"
          >
            {isRegister
              ? "Already have an account? Login"
              : "New user? Create an account"}
          </button>
        </div>

        {/* ✅ Footer brand updated */}
        <p className="text-xs text-center text-gray-400 mt-6">
          © TradeSecure
        </p>
      </div>
    </div>
  );
}

export default Login;
