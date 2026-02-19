import { Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import DocumentsList from "./pages/DocumentsList";
import DocumentDetails from "./pages/DocumentDetails";
import DocumentUpload from "./pages/DocumentUpload";
import Transactions from "./pages/Transactions";
import TransactionDetails from "./pages/TransactionDetails";
import Analytics from "./pages/Analytics";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      {/* ✅ Landing page (public) */}
      <Route path="/" element={<Landing />} />

      {/* ✅ Login route (public) */}
      <Route path="/login" element={<Login />} />

      {/* ✅ Dashboard (protected) */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* ✅ Documents list (protected) */}
      <Route
        path="/documents"
        element={
          <ProtectedRoute>
            <DocumentsList />
          </ProtectedRoute>
        }
      />

      {/* ✅ Document upload (protected) */}
      <Route
        path="/documents/upload"
        element={
          <ProtectedRoute>
            <DocumentUpload />
          </ProtectedRoute>
        }
      />

      {/* ✅ Document details (protected) */}
      <Route
        path="/documents/:id"
        element={
          <ProtectedRoute>
            <DocumentDetails />
          </ProtectedRoute>
        }
      />

      {/* ✅ Transactions list (protected) */}
      <Route
        path="/transactions"
        element={
          <ProtectedRoute>
            <Transactions />
          </ProtectedRoute>
        }
      />

      {/* ✅ Transaction details (protected) */}
      <Route
        path="/transactions/:id"
        element={
          <ProtectedRoute>
            <TransactionDetails />
          </ProtectedRoute>
        }
      />

      {/* ✅ Analytics dashboard (protected) */}
      <Route
        path="/analytics"
        element={
          <ProtectedRoute>
            <Analytics />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

