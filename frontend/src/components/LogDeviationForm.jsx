import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RotateCcw, Save, Search, Check } from 'lucide-react';
import { updateFormField, resetForm, saveDeviation } from '../store/deviationSlice';

export default function LogDeviationForm() {
  const dispatch = useDispatch();
  const { formFields, riskAssessment, formStatus, status } = useSelector(
    (state) => state.deviation
  );

  const handleChange = (field, value) => {
    dispatch(updateFormField({ field, value }));
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset the deviation form?')) {
      dispatch(resetForm());
    }
  };

  const handleSave = () => {
    if (!formFields.title || !formFields.detailed_description) {
      alert('Please ensure Title and Detailed Description are filled out before saving.');
      return;
    }
    dispatch(saveDeviation({ formFields, riskAssessment }));
  };

  const isSaving = status === 'loading';
  const descLength = (formFields.detailed_description || '').length;

  return (
    <div className="card">
      {/* Header */}
      <div className="form-header">
        <div>
          <h1 className="form-title">Log Deviation</h1>
          <p className="form-subtitle">
            Record any unexpected event, out-of-specification result or non-conformance.
          </p>
        </div>
        <div>
          {formStatus === 'Submitted' ? (
            <span className="badge-submitted">Submitted</span>
          ) : (
            <span className="badge-draft">Draft</span>
          )}
        </div>
      </div>

      {/* ── 1. DEVIATION INFORMATION ────────────────────────────── */}
      <div className="section-title">1. DEVIATION INFORMATION</div>

      <div className="form-grid" style={{ marginBottom: '16px' }}>
        {/* Site / Plant */}
        <div className="form-group">
          <label className="form-label" htmlFor="site_plant">
            Site / Plant <span className="req">*</span>
          </label>
          <select
            id="site_plant"
            className="select-field"
            value={formFields.site_plant || 'API Manufacturing Unit'}
            onChange={(e) => handleChange('site_plant', e.target.value)}
          >
            <option value="API Manufacturing Unit">API Manufacturing Unit</option>
            <option value="R&D Lab">R&D Lab</option>
            <option value="QC Lab">QC Lab</option>
            <option value="Warehouse">Warehouse</option>
            <option value="Packaging Unit">Packaging Unit</option>
          </select>
        </div>

        {/* Date of Occurrence */}
        <div className="form-group">
          <label className="form-label" htmlFor="date_of_occurrence">
            Date of Occurrence <span className="req">*</span>
          </label>
          <input
            id="date_of_occurrence"
            type="text"
            className="input-field"
            placeholder="dd-mm-yyyy"
            value={formFields.date_of_occurrence || ''}
            onChange={(e) => handleChange('date_of_occurrence', e.target.value)}
          />
        </div>
      </div>

      <div className="form-grid" style={{ marginBottom: '16px' }}>
        {/* Title / Short Description */}
        <div className="form-group">
          <label className="form-label" htmlFor="title">
            Title / Short Description <span className="req">*</span>
          </label>
          <input
            id="title"
            type="text"
            className="input-field"
            placeholder="e.g. OOS result for Assay in Batch ABC-001"
            value={formFields.title || ''}
            onChange={(e) => handleChange('title', e.target.value)}
          />
        </div>

        {/* Source */}
        <div className="form-group">
          <label className="form-label" htmlFor="source">
            Source <span className="req">*</span>
          </label>
          <select
            id="source"
            className="select-field"
            value={formFields.source || ''}
            onChange={(e) => handleChange('source', e.target.value)}
          >
            <option value="">Select source</option>
            <option value="Manufacturing">Manufacturing</option>
            <option value="QC Lab">QC Lab</option>
            <option value="Warehouse">Warehouse</option>
            <option value="Customer Complaint">Customer Complaint</option>
            <option value="Audit">Audit</option>
            <option value="Self-Inspection">Self-Inspection</option>
          </select>
        </div>
      </div>

      <div className="form-grid" style={{ marginBottom: '24px' }}>
        {/* Related Product / Material */}
        <div className="form-group">
          <label className="form-label" htmlFor="related_product">
            Related Product / Material
          </label>
          <div className="input-wrapper">
            <Search className="input-icon" size={16} />
            <input
              id="related_product"
              type="text"
              className="input-field"
              placeholder="Search product or material..."
              value={formFields.related_product || ''}
              onChange={(e) => handleChange('related_product', e.target.value)}
            />
          </div>
        </div>

        {/* Batch/Lot Number */}
        <div className="form-group">
          <label className="form-label" htmlFor="batch_lot_number">
            Batch/Lot Number
          </label>
          <input
            id="batch_lot_number"
            type="text"
            className="input-field"
            placeholder="Enter batch / lot no."
            value={formFields.batch_lot_number || ''}
            onChange={(e) => handleChange('batch_lot_number', e.target.value)}
          />
        </div>
      </div>

      {/* ── 2. DEVIATION DETAILS ─────────────────────────────────── */}
      <div className="section-title">2. DEVIATION DETAILS</div>

      {/* Detailed Description */}
      <div className="form-group" style={{ marginBottom: '16px' }}>
        <label className="form-label" htmlFor="detailed_description">
          Detailed Description <span className="req">*</span>
        </label>
        <textarea
          id="detailed_description"
          className="textarea-field"
          placeholder="Describe what happened, where, when and how it was detected..."
          rows={4}
          maxLength={2000}
          value={formFields.detailed_description || ''}
          onChange={(e) => handleChange('detailed_description', e.target.value)}
        />
        <div className="char-counter">{descLength}/2000</div>
      </div>

      <div className="form-grid">
        {/* Initial Impact */}
        <div className="form-group">
          <label className="form-label" htmlFor="initial_impact">
            Initial Impact <span className="req">*</span>
          </label>
          <select
            id="initial_impact"
            className="select-field"
            value={formFields.initial_impact || ''}
            onChange={(e) => handleChange('initial_impact', e.target.value)}
          >
            <option value="">Select impact</option>
            <option value="No Impact">No Impact</option>
            <option value="Minor">Minor</option>
            <option value="Moderate">Moderate</option>
            <option value="Major">Major</option>
            <option value="Critical">Critical</option>
          </select>
        </div>

        {/* Initial Severity */}
        <div className="form-group">
          <label className="form-label" htmlFor="initial_severity">
            Initial Severity <span className="req">*</span>
          </label>
          <select
            id="initial_severity"
            className="select-field"
            value={formFields.initial_severity || ''}
            onChange={(e) => handleChange('initial_severity', e.target.value)}
          >
            <option value="">Select severity</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
        </div>
      </div>

      {/* ── Form Actions ────────────────────────────────────────── */}
      <div className="form-actions">
        <button
          type="button"
          onClick={handleReset}
          className="btn-secondary"
          id="reset-form-btn"
        >
          <RotateCcw size={16} />
          <span>Reset Form</span>
        </button>

        <button
          type="button"
          onClick={handleSave}
          disabled={isSaving}
          className="btn-primary"
          id="save-deviation-btn"
        >
          <Save size={16} />
          <span>{isSaving ? 'Saving...' : 'Save Deviation'}</span>
        </button>
      </div>
    </div>
  );
}
