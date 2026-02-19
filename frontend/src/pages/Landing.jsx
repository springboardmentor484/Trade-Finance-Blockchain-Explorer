import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

export default function Landing() {
  const navigate = useNavigate();

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      navigate("/documents");
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex flex-col justify-between">
      {/* Navbar */}
      <nav className="bg-blue-800 bg-opacity-90 p-4 shadow-lg">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <div className="text-blue-600 font-bold text-xl">⚡</div>
            </div>
            <div className="text-white font-bold text-xl">Trade Finance Explorer</div>
          </div>
          <button
            onClick={() => navigate("/login")}
            className="bg-white text-blue-600 font-semibold px-6 py-2 rounded-lg hover:bg-gray-100"
          >
            Login
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-grow flex items-center justify-center px-4">
        <div className="text-center max-w-4xl">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Trade Finance Blockchain Explorer
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 mb-8">
            Secure, transparent, and compliant trade finance solutions with blockchain ledger integrity
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-lg p-6 text-white">
              <div className="text-4xl mb-2">🔐</div>
              <h3 className="text-xl font-bold mb-2">Secure Documentation</h3>
              <p className="text-blue-100">
                Cryptographically verified documents with immutable audit trails
              </p>
            </div>

            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-lg p-6 text-white">
              <div className="text-4xl mb-2">📊</div>
              <h3 className="text-xl font-bold mb-2">Real-time Analytics</h3>
              <p className="text-blue-100">
                Comprehensive risk scoring and compliance dashboards
              </p>
            </div>

            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-lg p-6 text-white">
              <div className="text-4xl mb-2">⛓️</div>
              <h3 className="text-xl font-bold mb-2">Blockchain Ledger</h3>
              <p className="text-blue-100">
                Transparent transaction history and document lifecycle tracking
              </p>
            </div>
          </div>

          {/* Features */}
          <div className="bg-white bg-opacity-5 backdrop-blur-md rounded-lg p-8 mb-12">
            <h2 className="text-3xl font-bold text-white mb-8">Key Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
              <div className="flex items-start space-x-3">
                <div className="text-2xl">✅</div>
                <div>
                  <h4 className="font-bold text-white mb-1">Document Management</h4>
                  <p className="text-blue-100 text-sm">Upload, verify, and track purchase orders, letters of credit, and invoices</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="text-2xl">✅</div>
                <div>
                  <h4 className="font-bold text-white mb-1">Trade Flow Automation</h4>
                  <p className="text-blue-100 text-sm">7-step transaction flow from PO creation to final payment</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="text-2xl">✅</div>
                <div>
                  <h4 className="font-bold text-white mb-1">Risk Scoring</h4>
                  <p className="text-blue-100 text-sm">User-based risk calculation using transaction history and compliance metrics</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="text-2xl">✅</div>
                <div>
                  <h4 className="font-bold text-white mb-1">Organization Insights</h4>
                  <p className="text-blue-100 text-sm">Aggregate metrics for volumes, status, and high-risk users</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="text-2xl">✅</div>
                <div>
                  <h4 className="font-bold text-white mb-1">Audit & Compliance</h4>
                  <p className="text-blue-100 text-sm">Complete ledger audit trails with document integrity verification</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="text-2xl">✅</div>
                <div>
                  <h4 className="font-bold text-white mb-1">Export Functionality</h4>
                  <p className="text-blue-100 text-sm">Generate CSV and PDF reports for documents and transactions</p>
                </div>
              </div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col md:flex-row justify-center gap-4">
            <button
              onClick={() => navigate("/login")}
              className="bg-white text-blue-600 font-bold px-8 py-3 rounded-lg hover:bg-gray-100 transition"
            >
              Login to Your Account
            </button>
            <button
              onClick={() => navigate("/login?signup=true")}
              className="bg-blue-500 text-white font-bold px-8 py-3 rounded-lg hover:bg-blue-400 transition border-2 border-white"
            >
              Sign Up Today
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-blue-900 bg-opacity-50 text-blue-100 text-center p-4">
        <p>&copy; 2026 Trade Finance Blockchain Explorer. All rights reserved.</p>
      </footer>
    </div>
  );
}
