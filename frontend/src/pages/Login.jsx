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
      //decode token
      const payload = JSON.parse(atob(res.data.access_token.split(".")[1]));
      localStorage.setItem("role", payload.role);
      localStorage.setItem("user_id", payload.user_id);
      window.location.href = "/profile";
    } catch (err) {
      console.log(err);
      alert("Invalid login");
    }
  };

  // return (
  //   <div>
  //     <h2>Login</h2>

  //     <input
  //       type="text"
  //       placeholder="Email"
  //       value={email}
  //       onChange={(e) => setEmail(e.target.value)}
  //     />

  //     <br /><br />

  //     <input
  //       type="password"
  //       placeholder="Password"
  //       value={password}
  //       onChange={(e) => setPassword(e.target.value)}
  //     />

  //     <br /><br />

  //     <button onClick={login}>Login</button>
  //   </div>
  // );

  return (
  <div className="min-h-screen flex items-center justify-center bg-gray-100">
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h2 className="text-2xl font-bold text-center mb-6">
        Login
      </h2>

      <input
        type="text"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full p-2 mb-4 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full p-2 mb-6 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <button
        onClick={login}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        Login
      </button>
    </div>
  </div>
);

}

export default Login;
