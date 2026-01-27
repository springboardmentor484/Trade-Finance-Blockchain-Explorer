import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DocumentUpload.css';

const DocumentUpload = ({ userRole, userId, accessToken }) => {
  const [formData, setFormData] = useState({
    doc_number: '',
    doc_type: 'PO',
    seller_id: '',
  });
  const [file, setFile] = useState(null);
  const [sellers, setSellers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadedDoc, setUploadedDoc] = useState(null);

  useEffect(() => {
    // Fetch sellers from the backend
    fetchSellers();
  }, []);

  const fetchSellers = async () => {
    try {
      const response = await axios.get('/api/users?role=corporate', {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setSellers(response.data);
    } catch (error) {
      console.error('Error fetching sellers:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('doc_number', formData.doc_number);
      formDataToSend.append('doc_type', formData.doc_type);
      if (formData.seller_id) {
        formDataToSend.append('seller_id', formData.seller_id);
      }
      formDataToSend.append('file', file);

      const response = await axios.post('/api/documents/upload', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${accessToken}`,
        },
      });

      setMessage(`✓ Document uploaded successfully! ID: ${response.data.id}`);
      setUploadedDoc(response.data);
      setFormData({ doc_number: '', doc_type: 'PO', seller_id: '' });
      setFile(null);
    } catch (error) {
      setMessage(`✗ Error uploading document: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (userRole !== 'corporate') {
    return <div className="upload-container"><p>Only buyers (corporate) can upload documents.</p></div>;
  }

  return (
    <div className="upload-container">
      <h2>Upload Purchase Order</h2>
      
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="doc_number">Document Number:</label>
          <input
            type="text"
            id="doc_number"
            name="doc_number"
            value={formData.doc_number}
            onChange={handleInputChange}
            placeholder="e.g., PO-2026-001"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="doc_type">Document Type:</label>
          <select
            id="doc_type"
            name="doc_type"
            value={formData.doc_type}
            onChange={handleInputChange}
          >
            <option value="PO">Purchase Order</option>
            <option value="BOL">Bill of Lading</option>
            <option value="INVOICE">Invoice</option>
            <option value="LOC">Letter of Credit</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="seller_id">Seller:</label>
          <select
            id="seller_id"
            name="seller_id"
            value={formData.seller_id}
            onChange={handleInputChange}
            required
          >
            <option value="">Select a seller...</option>
            {sellers.map(seller => (
              <option key={seller.id} value={seller.id}>
                {seller.name} ({seller.org_name})
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="file">Choose File:</label>
          <input
            type="file"
            id="file"
            onChange={handleFileChange}
            accept=".pdf,.doc,.docx,.xls,.xlsx"
            required
          />
        </div>

        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Uploading...' : 'Upload Document'}
        </button>
      </form>

      {message && (
        <div className={`message ${message.startsWith('✓') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {uploadedDoc && (
        <div className="upload-success">
          <h3>Document Details:</h3>
          <p><strong>ID:</strong> {uploadedDoc.id}</p>
          <p><strong>Doc Number:</strong> {uploadedDoc.doc_number}</p>
          <p><strong>Type:</strong> {uploadedDoc.doc_type}</p>
          <p><strong>Hash:</strong> {uploadedDoc.hash.substring(0, 16)}...</p>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
