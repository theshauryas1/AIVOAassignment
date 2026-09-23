import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { X, FileCheck, Calendar, Shield, ExternalLink } from 'lucide-react';
import { setSavedModalOpen, updateFormField } from '../store/deviationSlice';

export default function SavedDeviationsModal() {
  const dispatch = useDispatch();
  const { savedList, isSavedModalOpen } = useSelector((state) => state.deviation);

  if (!isSavedModalOpen) return null;

  const handleClose = () => {
    dispatch(setSavedModalOpen(false));
  };

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileCheck size={20} color="#2563eb" />
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>
              Saved Deviation Records ({savedList.length})
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="icon-btn"
            style={{ width: '32px', height: '32px' }}
          >
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {savedList.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#64748b' }}>
              No deviations recorded yet. Use the AI Deviation Assistant to extract and save your first record!
            </div>
          ) : (
            <table className="deviations-table">
              <thead>
                <tr>
                  <th>Deviation ID</th>
                  <th>Product</th>
                  <th>Batch / Lot</th>
                  <th>Date</th>
                  <th>Severity</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {savedList.map((dev) => (
                  <tr key={dev.id}>
                    <td style={{ fontWeight: 600, color: '#2563eb' }}>{dev.id}</td>
                    <td>{dev.related_product || 'N/A'}</td>
                    <td>
                      <code style={{ background: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>
                        {dev.batch_lot_number || 'N/A'}
                      </code>
                    </td>
                    <td>{dev.date_of_occurrence || 'N/A'}</td>
                    <td>
                      <span
                        className={`severity-pill ${
                          (dev.initial_severity || dev.ai_severity_classification || 'low').toLowerCase()
                        }`}
                      >
                        {dev.initial_severity || dev.ai_severity_classification || 'Low'}
                      </span>
                    </td>
                    <td>
                      <span className="badge-submitted" style={{ fontSize: '11px', padding: '2px 8px' }}>
                        {dev.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
