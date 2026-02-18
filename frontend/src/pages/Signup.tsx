import { useState } from "react";
import { signupUser } from "../api/auth";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const nav = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    org: "",
    role: "bank"
  });

  const handleChange = (e: any) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = async () => {
    try {
      await signupUser(form);
      alert("Signup successful");
      nav("/");
    } catch {
      alert("Signup failed");
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-xl font-bold mb-4">Signup</h1>

      {["name", "email", "password", "org"].map((f) => (
        <input
          key={f}
          name={f}
          type={f === "password" ? "password" : "text"}
          placeholder={f}
          onChange={handleChange}
          className="border p-2 w-full mb-2"
        />
      ))}

      <select
        name="role"
        onChange={handleChange}
        className="border p-2 w-full mb-4"
      >
        <option value="bank">Bank</option>
        <option value="coperate">Corporate</option>
        <option value="auditor">Auditor</option>
        <option value="admin">Admin</option>
      </select>

      <button
        onClick={handleSignup}
        className="bg-green-600 text-white px-4 py-2 w-full"
      >
        Signup
      </button>
    </div>
  );
}