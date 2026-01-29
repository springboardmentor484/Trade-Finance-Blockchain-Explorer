import { useState } from "react";
import api from "../services/api";

export default function UploadDocument() {
    const [docNumber, setDocNumber] = useState("");
    const [sellerId, setSellerId] = useState("");
    const[file, setFile] = useState(null);
    const [docType, setDocType] = useState("PO");


    const upload = async () => 
    {
        const token = localStorage.getItem("accessToken");
        const formData = new FormData();
        formData.append("file",file);
        try
        {
            await api.post("/upload", formData,
                {
                    params: {
                    doc_number: docNumber,
                    seller_id: sellerId,
                    doc_type: docType
                    }
,
                    headers: 
                    {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "multipart/form-data"
                    }
                });
            alert("Document uploaded successfully");
            window.location.href = "/documents";
        }
        catch
        {
            alert("Upload failed");
        }
    };
  //   return (
  //   <div>
  //     <h2>Upload Document</h2>

  //     <input
  //       placeholder="Document Number"
  //       value={docNumber}
  //       onChange={e => setDocNumber(e.target.value)}
  //     />

  //     <br /><br />

  //     <input
  //       placeholder="Seller ID"
  //       value={sellerId}
  //       onChange={e => setSellerId(e.target.value)}
  //     />

  //     <br /><br />
        
  //       <label>Document Type</label>
  //       <br />

  //       <select value={docType} onChange={e => setDocType(e.target.value)}>
  //       <option value="PO">Purchase Order (PO)</option>
  //       <option value="BOL">Bill of Lading (BOL)</option>
  //       <option value="LOC">Letter of Credit (LOC)</option>
  //       <option value="INVOICE">Invoice</option>
  //       </select>

  //       <br /><br />


  //     <input
  //       type="file"
  //       onChange={e => setFile(e.target.files[0])}
  //     />

  //     <br /><br />

  //     <button onClick={upload}>Upload</button>
  //   </div>
  // );



  return (
  <div className="min-h-screen flex items-center justify-center bg-gray-100">
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-lg">
      <h2 className="text-2xl font-bold mb-6 text-center">
        Upload Document
      </h2>

      {/* Document Number */}
      <div className="mb-4">
        <label className="block font-medium mb-1">
          Document Number
        </label>
        <input
          className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="PO-001"
          value={docNumber}
          onChange={e => setDocNumber(e.target.value)}
        />
      </div>

      {/* Seller ID */}
      <div className="mb-4">
        <label className="block font-medium mb-1">
          Seller ID
        </label>
        <input
          type="number"
          className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter Seller User ID"
          value={sellerId}
          onChange={e => setSellerId(e.target.value)}
        />
      </div>

      {/* Document Type */}
      <div className="mb-4">
        <label className="block font-medium mb-1">
          Document Type
        </label>
        <select
          className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={docType}
          onChange={e => setDocType(e.target.value)}
        >
          <option value="PO">Purchase Order (PO)</option>
          <option value="BOL">Bill of Lading (BOL)</option>
          <option value="LOC">Letter of Credit (LOC)</option>
          <option value="INVOICE">Invoice</option>
        </select>
      </div>

      {/* File Upload */}
      <div className="mb-6">
        <label className="block font-medium mb-1">
          Upload File
        </label>
        <input
          type="file"
          className="w-full"
          onChange={e => setFile(e.target.files[0])}
        />
      </div>

      {/* Submit Button */}
      <button
        onClick={upload}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        Upload Document
      </button>
    </div>
  </div>
  );

}