import { useEffect, useState } from "react";
import api from "../services/api";

export default function Profile() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    api.get("/user", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    .then(res => setUser(res.data))
    .catch(() => alert("Unauthorized"));
  }, []);

  if (!user) return <div>Loading...</div>;

  return (
    <div>
      <h2>Profile</h2>
      <p>Name: {user.name}</p>
      <p>Email: {user.email}</p>
      <p>Org: {user.org}</p>
      <p>Role: {user.role}</p>
    </div>
  );
}
