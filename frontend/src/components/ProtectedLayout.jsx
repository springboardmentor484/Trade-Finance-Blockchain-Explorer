import { Navigate } from "react-router-dom";
import Navbar from "./Navbar";

function ProtectedLayout({ children }) {
  const token = localStorage.getItem("accessToken");

  if (!token) {
    return <Navigate to="/" replace />;
  }

  return (
    <>
      <Navbar />
      <main className="p-6 bg-gray-50 min-h-screen">
        {children}
      </main>
    </>
  );
}

export default ProtectedLayout;
