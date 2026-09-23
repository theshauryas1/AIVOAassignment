import React, { useState, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Sparkles,
  FileText,
  UploadCloud,
  CheckCircle2,
  Bot,
  Send,
  ClipboardPaste,
  FileUp,
} from 'lucide-react';
import {
  processTextPrompt,
  processDocument,
} from '../store/deviationSlice';
import ExtractionProgress from './ExtractionProgress';
import RiskAssessmentCard from './RiskAssessmentCard';

export default function AIDeviationAssistant() {
  const dispatch = useDispatch();
  const fileInputRef = useRef(null);

  const { formFields, riskAssessment, aiMessage, status } = useSelector(
    (state) => state.deviation
  );

  const [promptText, setPromptText] = useState('');
  const [pasteNotesOpen, setPasteNotesOpen] = useState(false);
  const [notesContent, setNotesContent] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);

  const isProcessing = status === 'loading';

  // ── Handle File Selection / Upload ──────────────────────────────────────
  const handleFileUpload = (file) => {
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      alert('File exceeds 10MB limit.');
      return;
    }
    dispatch(processDocument(file));
  };

  const onFileInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) handleFileUpload(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileUpload(file);
  };

  // ── Handle Chat Prompt Submit ──────────────────────────────────────────
  const handleSendPrompt = (e) => {
    e?.preventDefault();
    const trimmed = promptText.trim();
    if (!trimmed || isProcessing) return;

    dispatch(
      processTextPrompt({
        message: trimmed,
        currentForm: formFields,
      })
    );
    setPromptText('');
  };

  // ── Handle Paste Notes Submit ──────────────────────────────────────────
  const handleExtractNotes = () => {
    const trimmed = notesContent.trim();
    if (!trimmed || isProcessing) return;

    dispatch(
      processTextPrompt({
        message: trimmed,
        currentForm: formFields,
      })
    );
    setNotesContent('');
    setPasteNotesOpen(false);
  };

  return (
    <div className="assistant-card">
      {/* Assistant Header */}
      <div className="assistant-header">
        <div className="assistant-icon-glow">
          <Sparkles size={18} />
        </div>
        <span className="assistant-title">AI Deviation Assistant</span>
        <span className="badge-beta">BETA</span>
      </div>

      {/* Drag & Drop File Upload Box */}
      <div
        className={`dropzone ${isDragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.csv,.xls,.xlsx,.png,.jpg,.jpeg"
          style={{ display: 'none' }}
          onChange={onFileInputChange}
        />
        <FileText className="dropzone-icon" />
        <p className="dropzone-text">
          Drag & drop supporting document here or <span className="link">click to browse</span>
        </p>
      </div>

      {/* OR Divider */}
      <div className="divider-or">
        <span>OR</span>
      </div>

      {/* Paste notes button / expandable area */}
      {!pasteNotesOpen ? (
        <button
          type="button"
          onClick={() => setPasteNotesOpen(true)}
          className="paste-notes-btn"
          id="paste-notes-toggle"
        >
          <ClipboardPaste size={16} />
          <span>Paste deviation details / notes</span>
        </button>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <textarea
            className="textarea-field"
            placeholder="Paste raw email, incident log, batch record extract, or inspection note here..."
            rows={3}
            value={notesContent}
            onChange={(e) => setNotesContent(e.target.value)}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <button
              type="button"
              className="btn-secondary"
              style={{ padding: '6px 12px', fontSize: '12px' }}
              onClick={() => setPasteNotesOpen(false)}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn-primary"
              style={{ padding: '6px 14px', fontSize: '12px' }}
              onClick={handleExtractNotes}
              disabled={isProcessing || !notesContent.trim()}
            >
              Extract with AI
            </button>
          </div>
        </div>
      )}

      {/* Supported Formats Banner */}
      <div className="supported-banner">
        <CheckCircle2 size={16} color="#16a34a" style={{ flexShrink: 0 }} />
        <span>Supported formats: PDF, DOCX, TXT, XLS, JPG, PNG &bull; Max file size: 10MB</span>
      </div>

      {/* Extraction Progress Component */}
      <ExtractionProgress />

      {/* AI Assistant Message Bubble */}
      <div className="ai-bubble">
        <Bot className="ai-bubble-icon" />
        <div style={{ flex: 1 }}>{aiMessage}</div>
      </div>

      {/* Risk Assessment Card */}
      <RiskAssessmentCard risk={riskAssessment} />

      {/* Chat Input Bar */}
      <form onSubmit={handleSendPrompt} className="chat-input-box">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask me anything about deviations..."
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)}
          disabled={isProcessing}
          id="ai-chat-input"
        />
        <button
          type="submit"
          className="chat-send-btn"
          disabled={isProcessing || !promptText.trim()}
          id="ai-send-btn"
          aria-label="Send to AI assistant"
        >
          <Send size={15} />
        </button>
      </form>

      {/* Disclaimer */}
      <p className="disclaimer-text">
        AI responses may contain errors. Please verify information.
      </p>
    </div>
  );
}
