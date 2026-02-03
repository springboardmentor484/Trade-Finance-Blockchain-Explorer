import { useEffect, useState } from "react";
import api from "../services/api";


export default function Documents() 
{
  const [documents, setDocuments] = useState([]);

  useEffect(() => 
    {
    const token = localStorage.getItem("accessToken");

    api.get("/documents", 
        {
            headers: 
          {
            Authorization: `Bearer ${token}`
          }
        })
    .then(res => setDocuments(res.data))
    .catch(() => alert("Unauthorized"));
    }, []);

//   return (
//     <div>
//       <h2 className="text-red-500">My Documents</h2>
//       {/* Upload button */}
//       <a href="/upload">
//         <button>Upload New Document</button>
//       </a>

//       <div style={{ marginTop: "20px" }}>
//         {documents.map(doc => (
//           <div
//             key={doc.id}
//             style={{
//               border: "1px solid #ccc",
//               padding: "15px",
//               marginBottom: "15px",
//               borderRadius: "6px"
//             }}
//           >
//             <p><strong>Document Number:</strong> {doc.doc_number}</p>
//             <p><strong>Document Type:</strong> {doc.doc_type}</p>
//             <p><strong>Status:</strong> {doc.status}</p>

//             <a href={`/document/${doc.id}`}>
//               <button>View Details</button>
//             </a>
//           </div>
//         ))}

//         {documents.length === 0 && (
//           <p>No documents available.</p>
//         )}
//       </div>
//     </div>
//   );
// }

return (
  <div className="p-6">
    <h2 className="text-2xl font-bold mb-4">My Documents</h2>

    {/* <a href="/upload">
      <button className="mb-6 px-4 py-2 bg-blue-600 text-white rounded">
        Upload New Document
      </button>
    </a> */}

    <div className="space-y-4">
      {documents.map(doc => (
        <div
          key={doc.id}
          className="border rounded-lg p-4 shadow-sm bg-white"
        >
          <p><span className="font-semibold">Document Number:</span> {doc.doc_number}</p>
          <p><span className="font-semibold">Type:</span> {doc.doc_type}</p>
          <p>
            <span className="font-semibold">Status:</span>{" "}
            <span className="text-blue-700">{doc.status}</span>
          </p>

          <a href={`/document/${doc.id}`}>
            <button className="mt-3 px-3 py-1 bg-gray-800 text-white rounded">
              View Details
            </button>
          </a>
        </div>
      ))}

      {documents.length === 0 && (
        <p className="text-gray-500">No documents available.</p>
      )}
    </div>
  </div>
);
}