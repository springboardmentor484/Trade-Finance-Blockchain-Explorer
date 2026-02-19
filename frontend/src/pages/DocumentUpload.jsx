import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDocument } from "../api/documents";
import { apiFetch } from "../api";

export default function DocumentUpload() {
  const navigate = useNavigate();
  const [docType, setDocType] = useState("PO");
  const [docNumber, setDocNumber] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [userInfo, setUserInfo] = useState(null);

  const handleLoad = async () => {
    const userResponse = await apiFetch("/users/");
    const userData = await userResponse.json();
    if (userResponse.ok) {
      setUserInfo(userData);
    }
  };

  useState(() => {
    handleLoad();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      if (!file) {
        throw new Error("Please select a file");
      }
      if (!docNumber) {
        throw new Error("Please enter document number");
      }

      const result = await uploadDocument(docType, docNumber, file);
      setSuccess("Document uploaded successfully!");
      setTimeout(() => navigate(`/documents/${result.id}`), 1500);
    } catch (err) {
      setError(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold text-white mb-2">📤 Upload Document</h1>
          <p className="text-blue-100">Add new trade finance documents to your account</p>
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
            onClick={() => navigate("/documents")}
            className="px-4 py-2 rounded-lg hover:bg-gray-100 font-semibold text-gray-700 transition"
          >
            📄 Documents
          </button>
          <button
            onClick={() => navigate("/transactions")}
            className="px-4 py-2 rounded-lg hover:bg-gray-100 font-semibold text-gray-700 transition"
          >
            📊 Transactions
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
      <div className="max-w-2xl mx-auto px-6 py-12">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-200">
          <div className="bg-gradient-to-r from-blue-50 to-cyan-50 px-8 py-8 border-b">
            <h2 className="text-2xl font-bold text-gray-900">Upload a Document</h2>
            <p className="text-gray-600 mt-2">Submit your purchase order, bill of lading, invoice, or letter of credit</p>
          </div>

          <div className="px-8 py-8">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-600 rounded">
                <p className="text-red-700 font-semibold">{error}</p>
              </div>
            )}

            {success && (
              <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-600 rounded">
                <p className="text-green-700 font-semibold">{success}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="form-group">
                <label htmlFor="docType" className="block text-sm font-semibold text-gray-700 mb-2">
                  Document Type
                </label>
                <select
                  id="docType"
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  disabled={loading}
                >
                  <option value="PO">Purchase Order</option>
                  <option value="BOL">Bill of Lading</option>
                  <option value="INVOICE">Invoice</option>
                  <option value="LC">Letter of Credit</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="docNumber" className="block text-sm font-semibold text-gray-700 mb-2">
                  Document Number
                </label>
                <input
                  id="docNumber"
                  type="text"
                  value={docNumber}
                  onChange={(e) => setDocNumber(e.target.value)}
                  placeholder="e.g., PO-2024-001"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="file" className="block text-sm font-semibold text-gray-700 mb-2">
                  Select File
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 cursor-pointer hover:border-blue-500 transition">
                  <input
                    id="file"
                    type="file"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="hidden"
                    disabled={loading}
                  />
                  <label htmlFor="file" className="cursor-pointer">
                    {file ? (
                      <div className="text-center">
                        <p className="text-lg font-semibold text-gray-900">✓ File selected</p>
                        <p className="text-sm text-gray-600 mt-1">{file.name}</p>
                        <p className="text-xs text-gray-500 mt-1">({(file.size / 1024).toFixed(2)} KB)</p>
                      </div>
                    ) : (
                      <div className="text-center">
                        <p className="text-lg font-semibold text-gray-900">📎 Click to upload file</p>
                        <p className="text-sm text-gray-600 mt-1">or drag and drop</p>
                      </div>
                    )}
                  </label>
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  disabled={loading || !file || !docNumber}
                  className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "Uploading..." : "Upload Document"}
                </button>
                <button
                  type="button"
                  onClick={() => navigate("/documents")}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
