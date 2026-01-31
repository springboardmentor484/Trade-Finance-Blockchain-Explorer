import { uploadDocument } from "../api/client";

export default function UploadDocument() {
  async function handleSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const token = localStorage.getItem("token");

    try {
      const res = await uploadDocument(formData, token);
      alert("Uploaded successfully! ID: " + res.document_id);
    } catch (err) {
      alert(err.message);
    }
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white shadow rounded">
      <h2 className="text-xl font-bold mb-4">Upload Document</h2>

      <form onSubmit={handleSubmit} className="space-y-3">
        <input name="doc_number" placeholder="Doc Number" className="input" />
        <input name="doc_type" placeholder="Doc Type" className="input" />
        <input name="seller_id" type="number" placeholder="Seller ID" className="input" />
        <input name="file" type="file" />

        <button className="bg-blue-600 text-white px-4 py-2 rounded">
          Upload
        </button>
      </form>
    </div>
  );
}