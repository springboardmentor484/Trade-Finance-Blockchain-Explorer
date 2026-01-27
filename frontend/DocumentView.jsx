import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DocumentView.css';

const DocumentView = ({ docId, userRole, userId, accessToken }) => {
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [performingAction, setPerformingAction] = useState(false);
  const [actionMessage, setActionMessage] = useState('');

  useEffect(() => {
    if (docId) {
      fetchDocumentDetails();
    }
  }, [docId]);

  const fetchDocumentDetails = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/documents/${docId}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setDocument(response.data);
      setError('');
    } catch (err) {
      setError(`Error loading document: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action) => {
    setPerformingAction(true);
    setActionMessage('');

    try {
      await axios.post(`/api/documents/action`, {
        doc_id: docId,
        action: action,
      }, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      setActionMessage(`✓ Action "${action}" recorded successfully`);
      // Refresh document
      setTimeout(() => fetchDocumentDetails(), 500);
    } catch (err) {
      setActionMessage(`✗ Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setPerformingAction(false);
    }
  };

  const downloadFile = async () => {
    try {
      const response = await axios.get(`/api/documents/file?file_url=${document.file_url}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', document.file_url);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
    } catch (err) {
      setError(`Error downloading file: ${err.message}`);
    }
  };

  const getAvailableActions = () => {
    if (!document) return [];

    const actions = [];

    if (userRole === 'corporate' && document.doc_type === 'BOL') {
      actions.push('RECEIVED');
    }

    if (userRole === 'corporate' && document.doc_type === 'PO') {
      actions.push('AMENDED');
    }

    if (userRole === 'auditor' && (document.doc_type === 'PO' || document.doc_type === 'LOC')) {
      actions.push('VERIFIED');
    }

    if (userRole === 'bank' && document.doc_type === 'INVOICE') {
      actions.push('PAID');
    }

    if (userRole === 'bank' && document.doc_type === 'PO') {
      actions.push('ISSUE_LOC');
    }

    // Seller actions
    if (userRole === 'corporate' && document.doc_type === 'PO') {
      // Assuming seller is also corporate
      actions.push('ISSUE_BOL');
    }

    if (userRole === 'corporate' && document.doc_type === 'BOL') {
      actions.push('SHIPPED');
      actions.push('ISSUE_INVOICE');
    }

    return [...new Set(actions)];
  };

  if (loading) return <div className="document-view"><p>Loading...</p></div>;
  if (error) return <div className="document-view error"><p>{error}</p></div>;
  if (!document) return <div className="document-view"><p>Document not found</p></div>;

  const availableActions = getAvailableActions();

  return (
    <div className="document-view">
      <div className="document-header">
        <h1>{document.doc_type}</h1>
        <p className="doc-number">Document: {document.doc_number}</p>
        <p className="doc-id">ID: {document.id}</p>
      </div>

      <div className="document-details">
        <div className="detail-section">
          <h3>Document Information</h3>
          <table>
            <tbody>
              <tr>
                <td><strong>Owner:</strong></td>
                <td>{document.owner_name}</td>
              </tr>
              <tr>
                <td><strong>Type:</strong></td>
                <td>{document.doc_type}</td>
              </tr>
              <tr>
                <td><strong>File:</strong></td>
                <td>
                  {document.file_url}
                  <button onClick={downloadFile} className="download-btn">Download</button>
                </td>
              </tr>
              <tr>
                <td><strong>Hash:</strong></td>
                <td className="hash">{document.hash}</td>
              </tr>
              <tr>
                <td><strong>Issued:</strong></td>
                <td>{new Date(document.issued_at).toLocaleString()}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="detail-section">
          <h3>Metadata</h3>
          <pre>{JSON.stringify(document.metadata, null, 2)}</pre>
        </div>

        {availableActions.length > 0 && (
          <div className="detail-section actions">
            <h3>Actions</h3>
            <div className="action-buttons">
              {availableActions.map(action => (
                <button
                  key={action}
                  onClick={() => handleAction(action)}
                  disabled={performingAction}
                  className="action-btn"
                >
                  {action}
                </button>
              ))}
            </div>
            {actionMessage && (
              <div className={`action-message ${actionMessage.startsWith('✓') ? 'success' : 'error'}`}>
                {actionMessage}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="timeline">
        <h3>Timeline</h3>
        <div className="timeline-entries">
          {document.ledger_entries.length === 0 ? (
            <p>No entries yet</p>
          ) : (
            document.ledger_entries.map((entry, index) => (
              <div key={entry.id} className="timeline-entry">
                <div className="timeline-marker"></div>
                <div className="timeline-content">
                  <div className="timeline-action">
                    <strong>{entry.action}</strong>
                    <span className="timeline-actor">{entry.actor_name} ({entry.actor_role})</span>
                  </div>
                  <div className="timeline-time">
                    {new Date(entry.created_at).toLocaleString()}
                  </div>
                  {Object.keys(entry.metadata).length > 0 && (
                    <div className="timeline-metadata">
                      <small>{JSON.stringify(entry.metadata)}</small>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentView;
