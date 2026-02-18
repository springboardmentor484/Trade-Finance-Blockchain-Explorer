import { useState } from "react";
import { uploadDocument } from "../api/documents";
import { useNavigate } from "react-router-dom";

export default function UploadDocument() {
  const nav = useNavigate();

  const [form, setForm] = useState({
    doc_number: "",
    doc_type: "INVOICE",
    seller_id: "",
    currency: "USD",
    amount: ""
  });

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: any) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleUpload = async () => {
    if (!file) return alert("Select a file");

    const fd = new FormData();
    Object.entries(form).forEach(([k, v]) => fd.append(k, v));
    fd.append("file", file);

    setLoading(true);
    try {
      await uploadDocument(fd);
      alert("Document uploaded");
      nav("/documents");
    } catch {
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-xl font-bold mb-4">Upload Document</h1>

      <input
        name="doc_number"
        placeholder="Document Number"
        className="border p-2 w-full mb-2"
        onChange={handleChange}
      />

      <select
        name="doc_type"
        className="border p-2 w-full mb-2"
        onChange={handleChange}
      >
        <option value="INVOICE">INVOICE</option>
        <option value="BOL">BOL</option>
        <option value="PO">PO</option>
        <option value="LOC">LOC</option>
      </select>

      <input
        name="seller_id"
        placeholder="Seller ID"
        className="border p-2 w-full mb-2"
        onChange={handleChange}
      />

      <input
        name="currency"
        placeholder="Currency"
        className="border p-2 w-full mb-2"
        onChange={handleChange}
      />

      <input
        name="amount"
        placeholder="Amount"
        type="number"
        className="border p-2 w-full mb-2"
        onChange={handleChange}
      />

      <input
        type="file"
        className="mb-4"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />

      <button
        disabled={loading}
        onClick={handleUpload}
        className="bg-blue-600 text-white px-4 py-2 w-full"
      >
        Upload
      </button>
    </div>
  );
}