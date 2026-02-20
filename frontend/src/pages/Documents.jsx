import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const role = localStorage.getItem("role");

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    api
      .get("/documents", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setDocuments(res.data))
      .catch(() => alert("Unauthorized"));
  }, []);

  const docIcon = (type) => {
    if (type === "PO") return "📝";
    if (type === "BOL") return "📦";
    if (type === "INVOICE") return "🧾";
    if (type === "LOC") return "🏦";
    return "📄";
  };

  const statusStyles = (status) => {
    if (status === "COMPLETED") return "border-l-green-500 bg-green-50/40 text-green-700";
    if (status === "DISPUTED") return "border-l-red-500 bg-red-50/40 text-red-700";
    if (status === "RECEIVED") return "border-l-emerald-500 bg-emerald-50/40 text-emerald-700";
    if (status === "SHIPPED") return "border-l-orange-500 bg-orange-50/40 text-orange-700";
    return "border-l-blue-500 bg-blue-50/40 text-blue-700";
  };

  return (
    <div className="p-8 max-w-6xl mx-auto bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">
            📄 My Documents
          </h2>
          <p className="text-sm text-gray-500">
            Track, verify, and manage trade documents
          </p>
        </div>

        {(role === "buyer" || role === "seller") && (
          <Link
            to="/upload"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition shadow"
          >
            + Upload Document
          </Link>
        )}
      </div>

      {/* Grid */}
      {documents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className={`border-l-4 rounded-2xl p-5 bg-white shadow-sm hover:shadow-lg hover:scale-[1.01] transition transform ${statusStyles(doc.status)}`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{docIcon(doc.doc_type)}</span>
                  <div>
                    <p className="text-lg font-semibold text-gray-800">
                      {doc.doc_number}
                    </p>
                    <p className="text-sm text-gray-500">
                      {doc.doc_type}
                    </p>
                  </div>
                </div>

                {/* Status badge */}
                <span className="px-2.5 py-1 text-xs rounded-full font-semibold bg-white border shadow-sm">
                  {doc.status}
                </span>
              </div>

              {doc.is_compromised && (
                <div className="mt-3 text-sm text-red-600 font-medium flex items-center gap-1">
                  ⚠ Integrity issue detected
                </div>
              )}

              <div className="mt-4 flex justify-between items-center">
                <Link
                  to={`/document/${doc.id}`}
                  className="text-blue-600 hover:underline text-sm font-medium"
                >
                  View details →
                </Link>

                <span className="text-xs text-gray-400">
                  #{doc.id}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white border rounded-2xl p-10 text-center shadow-sm">
          <p className="text-gray-600 mb-3">
            No documents available yet.
          </p>

          {(role === "buyer" || role === "seller") && (
            <Link
              to="/upload"
              className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Upload your first document
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
