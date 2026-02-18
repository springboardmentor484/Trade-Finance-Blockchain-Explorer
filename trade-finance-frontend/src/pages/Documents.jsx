import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, Check, AlertCircle } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploadFormData, setUploadFormData] = useState({
    doc_number: '',
    doc_type: 'PO',
    seller_id: '',
    file: null
  });
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const DOC_TYPES = ['PO', 'LOC', 'BILL_OF_LADING', 'INVOICE', 'COO', 'INSURANCE_CERT'];

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/documents/documents`);
      setDocuments(response.data.documents || []);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
      setError('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadChange = (e) => {
    const { name, value } = e.target;
    setUploadFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    setUploadFormData(prev => ({
      ...prev,
      file: e.target.files[0]
    }));
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    setUploadError(null);

    if (!uploadFormData.doc_number || !uploadFormData.file) {
      setUploadError('Please fill in all fields');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('doc_number', uploadFormData.doc_number);
      formData.append('doc_type', uploadFormData.doc_type);
      formData.append('seller_id', uploadFormData.seller_id || '1');
      formData.append('file', uploadFormData.file);

      const response = await axios.post(
        `${API_BASE_URL}/documents/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      // Add new document to list
      setDocuments(prev => [{
        id: response.data.id,
        doc_number: response.data.doc_number,
        doc_type: response.data.doc_type,
        owner_id: 1,
        file_hash: response.data.file_hash,
        created_at: new Date().toISOString()
      }, ...prev]);

      // Reset form
      setUploadFormData({
        doc_number: '',
        doc_type: 'PO',
        seller_id: '',
        file: null
      });
      setShowUploadForm(false);
    } catch (err) {
      setUploadError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-600">Loading documents...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <button
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
          >
            <Upload size={20} />
            {showUploadForm ? 'Cancel' : 'Upload Document'}
          </button>
        </div>

        {/* Upload Form */}
        {showUploadForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Upload New Document</h2>

            {uploadError && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
                <p className="text-red-700 text-sm">{uploadError}</p>
              </div>
            )}

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Document Number
                  </label>
                  <input
                    type="text"
                    name="doc_number"
                    value={uploadFormData.doc_number}
                    onChange={handleUploadChange}
                    placeholder="PO-2024-001"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Document Type
                  </label>
                  <select
                    name="doc_type"
                    value={uploadFormData.doc_type}
                    onChange={handleUploadChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {DOC_TYPES.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  File
                </label>
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={uploading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
              >
                {uploading ? 'Uploading...' : 'Upload Document'}
              </button>
            </form>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 p-4 rounded-lg text-red-700 mb-8">
            {error}
          </div>
        )}

        {/* Documents List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {documents.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <FileText size={48} className="mx-auto mb-4 opacity-50" />
              <p>No documents found. Start by uploading one.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Document Number
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Hash
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id} className="border-b hover:bg-gray-50">
                      <td className="px-6 py-4 font-medium text-gray-900">
                        {doc.doc_number}
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                          {doc.doc_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 font-mono">
                        <span className="text-xs">{doc.file_hash?.substring(0, 12)}...</span>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <button className="text-blue-600 hover:text-blue-800 font-medium">
                          View Ledger
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
