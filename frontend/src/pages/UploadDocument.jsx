import { useState } from "react";
import api from "../services/api";

export default function UploadDocument() {
  const [docNumber, setDocNumber] = useState("");
  const [sellerId, setSellerId] = useState("");
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const role = localStorage.getItem("role");

  // 🔒 UI Role Guard
  if (role === "auditor" || role === "bank") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md text-center">
          <h2 className="text-xl font-semibold mb-2">Access Restricted</h2>
          <p className="text-gray-600">
            Your role is not allowed to upload documents.
            Auditors and banks can only review and verify.
          </p>
        </div>
      </div>
    );
  }

  const upload = async () => {
    setError("");

    if (!docNumber || !sellerId || !file || !docType) {
      setError("Please fill all fields and select a file.");
      return;
    }

    const token = localStorage.getItem("accessToken");
    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      await api.post("/upload", formData, {
        params: {
          doc_number: docNumber,
          seller_id: sellerId,
          doc_type: docType,
        },
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      alert("✅ Document uploaded successfully");
      window.location.href = "/documents";
    } catch (err) {
      console.error(err);
      setError("❌ Upload failed. Please check inputs and try again.");
    } finally {
      setLoading(false);
    }
  };

  // 🔽 Role-based document types
  const docTypeOptions =
    role === "buyer"
      ? [{ value: "PO", label: "Purchase Order (PO)" }]
      : [
          { value: "BOL", label: "Bill of Lading (BOL)" },
          { value: "INVOICE", label: "Invoice" },
        ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-lg">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">
          Upload Document
        </h2>

        {error && (
          <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        <div className="mb-4">
          <label className="block font-medium mb-1 text-gray-700">
            Document Number
          </label>
          <input
            className="w-full p-2 border rounded"
            placeholder="PO-001"
            value={docNumber}
            onChange={(e) => setDocNumber(e.target.value)}
          />
        </div>

        <div className="mb-4">
          <label className="block font-medium mb-1 text-gray-700">
            Seller User ID
          </label>
          <input
            type="number"
            className="w-full p-2 border rounded"
            placeholder="e.g. 4"
            value={sellerId}
            onChange={(e) => setSellerId(e.target.value)}
          />
        </div>

        <div className="mb-4">
          <label className="block font-medium mb-1 text-gray-700">
            Document Type
          </label>
          <select
            className="w-full p-2 border rounded"
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
          >
            <option value="">Select document type</option>
            {docTypeOptions.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="mb-6">
          <label className="block font-medium mb-1 text-gray-700">
            Upload File
          </label>
          <input
            type="file"
            className="w-full"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>

        <button
          onClick={upload}
          disabled={loading}
          className={`w-full py-2 rounded text-white ${
            loading ? "bg-gray-400" : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {loading ? "Uploading..." : "Upload Document"}
        </button>
      </div>
    </div>
  );
}
