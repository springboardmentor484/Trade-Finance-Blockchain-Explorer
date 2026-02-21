import { Navigate } from "react-router-dom";
import { getToken } from "../api/auth";
import Navbar from "./Navbar";

export default function ProtectedRoute({ children }) {
  const token = getToken();
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
}
