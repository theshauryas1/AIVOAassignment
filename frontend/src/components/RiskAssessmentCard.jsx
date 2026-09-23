import React from 'react';
import { ShieldAlert, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function RiskAssessmentCard({ risk }) {
  if (!risk || !risk.severity_classification) {
    return null;
  }

  const severity = risk.severity_classification.toLowerCase();

  const getPillClass = () => {
    if (severity.includes('critical')) return 'critical';
    if (severity.includes('high') || severity.includes('major')) return 'high';
    if (severity.includes('medium') || severity.includes('moderate')) return 'medium';
    return 'low';
  };

  return (
    <div className="risk-card">
      <div className="risk-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <ShieldAlert size={16} color="#4b5563" />
          <span className="risk-title">AI Copilot Risk Assessment</span>
        </div>
        <span className={`severity-pill ${getPillClass()}`}>
          {risk.severity_classification} Severity
        </span>
      </div>

      {risk.impact_assessment && (
        <div className="risk-item">
          <span className="risk-item-label">Impact Assessment:</span>
          <p className="risk-item-val">{risk.impact_assessment}</p>
        </div>
      )}

      {risk.suggested_next_action && (
        <div className="risk-item">
          <span className="risk-item-label">Suggested Next Action:</span>
          <p className="risk-item-val" style={{ color: '#1d4ed8', fontWeight: 500 }}>
            {risk.suggested_next_action}
          </p>
        </div>
      )}

      {risk.risk_reasoning && (
        <div className="risk-item">
          <span className="risk-item-label">Risk Reasoning:</span>
          <p className="risk-item-val">{risk.risk_reasoning}</p>
        </div>
      )}

      {risk.regulatory_risk && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
          <span className="risk-item-label" style={{ fontSize: '12px' }}>Regulatory Reporting Required:</span>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 600,
              padding: '2px 8px',
              borderRadius: '4px',
              background: risk.regulatory_risk.toLowerCase() === 'yes' ? '#fee2e2' : '#f0fdf4',
              color: risk.regulatory_risk.toLowerCase() === 'yes' ? '#dc2626' : '#166534',
            }}
          >
            {risk.regulatory_risk}
          </span>
        </div>
      )}
    </div>
  );
}
