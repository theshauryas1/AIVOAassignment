import React from 'react';
import { useSelector } from 'react-redux';

export default function ExtractionProgress() {
  const { progress, progressMessage, status } = useSelector((state) => state.deviation);

  if (status !== 'loading' && progress === 0) {
    return null;
  }

  return (
    <div className="progress-container">
      <div className="progress-header">
        <span className="progress-label">Extraction Progress</span>
        <span className="progress-pct">{progress}%</span>
      </div>
      <div className="progress-bar-bg">
        <div
          className="progress-bar-fill"
          style={{ width: `${progress}%` }}
        />
      </div>
      {progressMessage && (
        <span className="progress-desc">
          {progressMessage}
        </span>
      )}
    </div>
  );
}
