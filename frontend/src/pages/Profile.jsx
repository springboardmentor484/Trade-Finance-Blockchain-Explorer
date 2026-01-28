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

  // if (!user) return <div>Loading...</div>;

  // return (
  //   <div>
  //     <h2>Profile</h2>
  //     <p>Name: {user.name}</p>
  //     <p>Email: {user.email}</p>
  //     <p>Org: {user.org}</p>
  //     <p>Role: {user.role}</p>
  //   </div>
  // );

  if (!user) return (
  <div className="min-h-screen flex items-center justify-center">
    Loading...
  </div>
  );

  // logout function
  const logout = () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("role");
  localStorage.removeItem("user_id");

  window.location.href = "/";
  };


return (
  <div className="min-h-screen flex items-center justify-center bg-gray-100">
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h2 className="text-2xl font-bold mb-6 text-center">
        Profile
      </h2>

      <div className="space-y-3">
        <p>
          <span className="font-semibold">Name:</span> {user.name}
        </p>
        <p>
          <span className="font-semibold">Email:</span> {user.email}
        </p>
        <p>
          <span className="font-semibold">Organization:</span> {user.org}
        </p>
        <p>
          <span className="font-semibold">Role:</span>{" "}
          <span className="text-blue-600">{user.role}</span>
        </p>
      </div>

      <div className="mt-6 flex justify-center space-x-4">
  <a href="/documents">
    <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
      My Documents
    </button>
  </a>

  <a href="/upload">
    <button className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-900">
      Upload Document
    </button>
  </a>

  <button
    onClick={logout}
    className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
  >
    Logout
  </button>
</div>



    </div>
  </div>
);

}
