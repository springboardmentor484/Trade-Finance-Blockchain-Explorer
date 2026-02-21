import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const res = await loginUser({ email, password });

      // 1️⃣ Save access token
      localStorage.setItem("accessToken", res.access_token);

      // 2️⃣ Redirect
      navigate("/documents");
    } catch (err) {
      console.error("LOGIN FAILED:", err);
      alert("Invalid email or password");
    }
  };

  return (
    <div className="p-10 max-w-sm mx-auto">
      <h1 className="text-2xl mb-4">Login</h1>

      <input
        className="border p-2 block mb-2 w-full"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        className="border p-2 block mb-4 w-full"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button
        onClick={handleLogin}
        className="bg-blue-500 text-white px-4 py-2 w-full"
      >
        Login
      </button>
    </div>
  );
}