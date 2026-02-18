import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, Check, AlertCircle, X, Eye } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const Documents = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [showLedgerModal, setShowLedgerModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [ledgerData, setLedgerData] = useState(null);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [accessDenied, setAccessDenied] = useState(null);
  const [uploadFormData, setUploadFormData] = useState({
    doc_number: '',
    doc_type: 'PO',
    seller_id: '',
    file: null
  });
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const DOC_TYPES = ['PO', 'LOC', 'BILL_OF_LADING', 'INVOICE', 'COO', 'INSURANCE_CERT'];

  // Helper to safely format dates
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return dateString; // Return original string if invalid
      }
      return date.toLocaleString();
    } catch (e) {
      return dateString; // Return original string if parsing fails
    }
  };

  // Helper to check if user can view this document
  const canViewDocument = (doc) => {
    if (!user) return false;
    const userRole = user.role.toLowerCase();
    
    // AUDITOR, ADMIN, BANK can view all documents
    if (['auditor', 'admin', 'bank'].includes(userRole)) {
      return true;
    }
    
    // CORPORATE can only view their own documents
    if (userRole === 'corporate' && doc.owner_id === user.id) {
      return true;
    }
    
    return false;
  };

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

  const viewLedger = async (doc) => {
    if (!canViewDocument(doc)) {
      setAccessDenied(`You don't have permission to view this document's ledger.`);
      return;
    }

    setSelectedDocument(doc);
    setLedgerLoading(true);
    setAccessDenied(null);

    try {
      const response = await axios.get(`${API_BASE_URL}/documents/${doc.id}`);
      setLedgerData(response.data);
      setShowLedgerModal(true);
    } catch (err) {
      if (err.response?.status === 403) {
        setAccessDenied('You do not have permission to view this document.');
      } else {
        setAccessDenied('Failed to load document ledger');
      }
    } finally {
      setLedgerLoading(false);
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
        owner_id: user?.id || 1,
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

        {/* Ledger Modal */}
        {showLedgerModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 flex justify-between items-center p-6 border-b bg-white">
                <h2 className="text-2xl font-bold text-gray-900">
                  Document Ledger: {selectedDocument?.doc_number}
                </h2>
                <button
                  onClick={() => {
                    setShowLedgerModal(false);
                    setLedgerData(null);
                    setAccessDenied(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={24} />
                </button>
              </div>

              {ledgerLoading && (
                <div className="p-6 text-center text-gray-600">
                  Loading ledger...
                </div>
              )}

              {accessDenied && (
                <div className="p-6">
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 flex items-start gap-3">
                    <AlertCircle className="text-orange-600 flex-shrink-0 mt-0.5" size={20} />
                    <p className="text-orange-700">{accessDenied}</p>
                  </div>
                </div>
              )}

              {!ledgerLoading && ledgerData && !accessDenied && (
                <div className="p-6 space-y-4">
                  {/* Document Info */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-3">Document Information</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Document Number</p>
                        <p className="font-medium text-gray-900">{ledgerData.doc_number}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Type</p>
                        <p className="font-medium text-gray-900">{ledgerData.doc_type}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">File Hash (SHA-256)</p>
                        <p className="font-mono text-xs bg-white p-2 rounded border border-gray-200 break-all">
                          {ledgerData.file_hash}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Created</p>
                        <p className="font-medium text-gray-900">
                          {formatDate(ledgerData.created_at)}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Audit Trail / Ledger */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Audit Trail</h3>
                    {ledgerData.ledger && ledgerData.ledger.length > 0 ? (
                      <div className="space-y-2">
                        {ledgerData.ledger.map((entry, idx) => (
                          <div key={idx} className="p-4 bg-gray-50 rounded-lg border-l-4 border-blue-500">
                            <div className="flex justify-between items-start">
                              <div>
                                <p className="font-semibold text-gray-900">
                                  {entry.action}
                                </p>
                                <p className="text-sm text-gray-600">
                                  By: {entry.actor_role?.toUpperCase()}
                                </p>
                              </div>
                              <p className="text-xs text-gray-500">
                                {formatDate(entry.created_at)}
                              </p>
                            </div>
                            {entry.additional_metadata && Object.keys(entry.additional_metadata).length > 0 && (
                              <p className="text-xs text-gray-500 mt-2 font-mono">
                                {JSON.stringify(entry.additional_metadata)}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-600 text-center py-4">No ledger entries yet</p>
                    )}
                  </div>
                </div>
              )}
            </div>
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
                        {canViewDocument(doc) ? (
                          <button
                            onClick={() => viewLedger(doc)}
                            className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium"
                          >
                            <Eye size={16} /> View Ledger
                          </button>
                        ) : (
                          <span className="text-gray-400 text-xs">No access</span>
                        )}
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


