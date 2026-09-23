import React from 'react';
import { useDispatch } from 'react-redux';
import { Bell, ChevronDown, Building2, ListOrdered } from 'lucide-react';
import { setSavedModalOpen, fetchDeviations } from '../store/deviationSlice';

export default function Navbar() {
  const dispatch = useDispatch();

  const handleOpenSaved = () => {
    dispatch(fetchDeviations());
    dispatch(setSavedModalOpen(true));
  };

  return (
    <header className="navbar">
      <div className="nav-left">
        {/* Brand Logo */}
        <a href="#" className="brand-logo">
          <svg className="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M12 2L2 22h20L12 2z" fill="#2563eb" stroke="#2563eb" />
            <path d="M12 8l5 11H7l5-11z" fill="#ffffff" />
          </svg>
          <div className="brand-text">
            <span className="brand-title">AIVOA</span>
            <span className="brand-subtitle">AI for a Safer Tomorrow</span>
          </div>
        </a>

        {/* Navigation Tabs */}
        <nav className="nav-links">
          <span className="nav-item">QMS</span>
          <span className="nav-item">Dashboard</span>
          <span className="nav-item active">Deviations</span>
          <span className="nav-item">CAPAs</span>
          <span className="nav-item">Change Control</span>
          <span className="nav-item">Audits</span>
          <span className="nav-item">Documents</span>
          <span className="nav-item">Reports</span>
        </nav>
      </div>

      {/* Right Controls */}
      <div className="nav-right">
        {/* Saved Deviations Button */}
        <button
          onClick={handleOpenSaved}
          className="btn-secondary"
          style={{ padding: '6px 12px', fontSize: '12.5px', gap: '6px' }}
          title="View all saved deviations in database"
        >
          <ListOrdered size={15} />
          <span>Records</span>
        </button>

        {/* Plant / Site Selector */}
        <div className="plant-selector">
          <Building2 size={16} color="#64748b" />
          <span>Vasudha Pharma Chem Limited</span>
          <ChevronDown size={14} color="#64748b" />
        </div>

        {/* Notification Bell */}
        <button className="icon-btn" aria-label="Notifications">
          <Bell size={18} />
          <span className="badge-dot"></span>
        </button>

        {/* User Avatar */}
        <div className="user-avatar" title="Mohit H. (Quality Head)">
          MH
        </div>
      </div>
    </header>
  );
}
