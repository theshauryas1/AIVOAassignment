import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { CheckCircle2 } from 'lucide-react';
import Navbar from './components/Navbar';
import LogDeviationForm from './components/LogDeviationForm';
import AIDeviationAssistant from './components/AIDeviationAssistant';
import SavedDeviationsModal from './components/SavedDeviationsModal';
import { clearToast, fetchDeviations } from './store/deviationSlice';

export default function App() {
  const dispatch = useDispatch();
  const { toast } = useSelector((state) => state.deviation);

  useEffect(() => {
    dispatch(fetchDeviations());
  }, [dispatch]);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => {
        dispatch(clearToast());
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [toast, dispatch]);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />

      <main className="app-container">
        {/* Left: Log Deviation Form */}
        <LogDeviationForm />

        {/* Right: AI Deviation Assistant */}
        <AIDeviationAssistant />
      </main>

      {/* Modal for Saved Deviations */}
      <SavedDeviationsModal />

      {/* Floating Toast Notification */}
      {toast && (
        <div className="toast">
          <CheckCircle2 size={18} />
          <span>{toast}</span>
        </div>
      )}
    </div>
  );
}
