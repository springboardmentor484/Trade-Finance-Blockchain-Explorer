import { useEffect, useState } from "react";
import { fetchDocuments } from "../api/documents";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api";

export default function DocumentsList() {
  const [docs, setDocs] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      
      // Fetch user profile
      const userResponse = await apiFetch("/users/");
      const userData = await userResponse.json();
      if (userResponse.ok) {
        setUserInfo(userData);
      }
      
      // Fetch documents
      const data = await fetchDocuments();
      setDocs(data);
      setError("");
    } catch (e) {
      console.error("Failed to fetch data:", e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading documents...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold text-white mb-2">📄 Documents</h1>
          <p className="text-blue-100">Manage and track your trade finance documents</p>
          {userInfo && (
            <div className="mt-4 text-blue-100 text-sm">
              Logged in as: <span className="font-semibold">{userInfo.name}</span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center space-x-8">
          <button
            onClick={() => navigate("/transactions")}
            className="px-4 py-2 rounded-lg hover:bg-gray-100 font-semibold text-gray-700 transition"
          >
            📊 Transactions
          </button>
          <button
            onClick={() => navigate("/dashboard")}
            className="px-4 py-2 rounded-lg hover:bg-gray-100 font-semibold text-gray-700 transition"
          >
            📈 Dashboard
          </button>
          <button
            onClick={() => {
              localStorage.clear();
              navigate("/login");
            }}
            className="px-4 py-2 rounded-lg hover:bg-gray-100 font-semibold text-gray-700 transition ml-auto"
          >
            🚪 Logout
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-600 rounded">
            <p className="text-red-700 font-semibold">Error: {error}</p>
            <button
              className="mt-3 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 font-semibold"
              onClick={loadData}
            >
              Retry
            </button>
          </div>
        )}

        {/* Header with Upload Button */}
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Your Documents</h2>
          <button
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold shadow-md hover:shadow-lg transition"
            onClick={() => navigate("/documents/upload")}
          >
            + Upload Document
          </button>
        </div>

        {docs.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <p className="text-lg text-gray-600 mb-4">No documents uploaded yet.</p>
            <button
              onClick={() => navigate("/documents/upload")}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold"
            >
              Upload your first document
            </button>
          </div>
        ) : (
          <div className="grid gap-6">
            {docs.map((doc) => (
              <div
                key={doc.id}
                onClick={() => navigate(`/documents/${doc.id}`)}
                className="bg-white rounded-lg border border-gray-200 p-6 cursor-pointer hover:shadow-lg hover:border-blue-300 transition-all duration-200"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg text-gray-900 mb-2">
                      {doc.doc_type} — {doc.doc_number}
                    </h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Status:{" "}
                      <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700">
                        {doc.status}
                      </span>
                    </p>
                    <p className="text-xs text-gray-500">
                      Uploaded: {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    className="bg-blue-100 text-blue-700 px-4 py-2 rounded-lg text-sm hover:bg-blue-200 font-semibold transition"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/documents/${doc.id}`);
                    }}
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
