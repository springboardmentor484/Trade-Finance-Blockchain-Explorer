import { useState } from "react";
import api from "../services/api";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const login = async () => {
    try {
      const res = await api.post("/login", null, {
        params: {
          email: email,
          password: password
        }
      });

      localStorage.setItem("accessToken", res.data.access_token);
      window.location.href = "/profile";
    } catch (err) {
      console.log(err);
      alert("Invalid login");
    }
  };

  return (
    <div>
      <h2>Login</h2>

      <input
        type="text"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <br /><br />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <br /><br />

      <button onClick={login}>Login</button>
    </div>
  );
}

export default Login;
