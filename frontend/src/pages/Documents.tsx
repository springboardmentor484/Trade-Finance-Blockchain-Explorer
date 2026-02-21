import { useEffect, useState } from "react";
import api from "../api/client";
import { useNavigate } from "react-router-dom";

export default function Documents() {
  const [documents, setDocuments] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/documents/")
      .then(res => setDocuments(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Documents</h1>

      {/* ✅ STEP 4: UPLOAD BUTTON */}
      <button
        onClick={() => navigate("/upload")}
        className="bg-green-600 text-white px-4 py-2 mb-4 rounded"
      >
        Upload Document
      </button>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th className="p-2">Doc No</th>
            <th className="p-2">Type</th>
            <th className="p-2">Owner</th>
            <th className="p-2">Action</th>
          </tr>
        </thead>

        <tbody>
          {documents.map(doc => (
            <tr key={doc.id} className="border">
              <td className="p-2">{doc.doc_number}</td>
              <td className="p-2">{doc.doc_type}</td>
              <td className="p-2">{doc.owner_id}</td>
              <td className="p-2">
                <button
                  className="text-blue-600"
                  onClick={() => navigate(`/ledger/${doc.id}`)}
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}