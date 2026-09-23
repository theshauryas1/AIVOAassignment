# AIVOA AI-Powered Deviation Intake Module – Demo & Video Presentation Guide

This guide provides the exact script and workflow for your **5–10 minute submission demo video**.

---

## 🚀 How to Run the Application

### 1. Start the Backend
Open a terminal in `d:\assignment\backend`:
```bash
# (Optional) Add your GROQ_API_KEY in backend/.env if you have one.
# If not provided, the app uses an intelligent pharma heuristic pipeline so the demo works smoothly!
uvicorn main:app --reload --port 8000
```
Backend will be live at: `http://localhost:8000` (API documentation at `http://localhost:8000/docs`)

### 2. Start the Frontend
Open a second terminal in `d:\assignment\frontend`:
```bash
npm run dev
```
Frontend will be live at: `http://localhost:5173`

---

## 🎬 5–10 Minute Demo Video Walkthrough Script

### Part 1: Product Overview (0:00 – 1:30)
1. **Show the UI**: Point out how closely it matches the AIVOA enterprise design reference:
   - Header with QMS tabs, company selector (*Vasudha Pharma Chem Limited*), notifications, user profile.
   - Left panel: **Log Deviation** form with two formal sections:
     - 1. DEVIATION INFORMATION (Site/Plant, Date of Occurrence, Title, Source, Related Product, Batch/Lot)
     - 2. DEVIATION DETAILS (Detailed Description, Initial Impact, Initial Severity)
     - Action buttons: *Reset Form* and *Save Deviation*
   - Right panel: **AI Deviation Assistant** (Dropzone, Paste Notes, Progress Bar, AI Chat, Risk Assessment Card).
2. **Key rule**: Emphasize that in compliance with the assignment instructions, **the left form is never manually filled**; all data is populated via the AI panel on the right.

---

### Part 2: AI Tool 1 – Log Deviation via Natural Language Prompt (1:30 – 3:00)
1. In the right panel chat input (*"Ask me anything about deviations..."*), type or paste:
   ```text
   API Manufacturing Unit reported temperature spike to 48.5°C during crystallization of Metformin Hydrochloride API batch MFH260712A on 14-08-2024
   ```
2. Click **Send** (blue arrow button).
3. **Show what happens**:
   - The animated **Extraction Progress** bar appears and tracks progress.
   - The AI Assistant message updates with a response.
   - The left **Log Deviation** form automatically populates:
     - Site/Plant: *API Manufacturing Unit*
     - Date: *14-08-2024*
     - Product: *Metformin Hydrochloride API*
     - Batch: *MFH260712A*
     - Source: *Manufacturing*
     - Description: Full event narrative
     - Initial Impact: *Major*
     - Initial Severity: *High*
   - The **AI Copilot Risk Assessment Card** appears below the chat with:
     - Severity: *High Severity* (orange pill)
     - Impact Assessment: *Potential impact on API batch critical quality attributes (CQA)...*
     - Suggested Next Action: *1. Quarantine batch... 2. Initiate QA Root Cause Analysis... 3. Test sample...*
     - Risk Reasoning: *Evaluated according to ICH Q7 GMP guidelines.*
     - Regulatory Risk: *Yes*

---

### Part 3: AI Tool 2 – Edit Deviation via Conversational Correction (3:00 – 4:30)
1. In the chat input, simulate a correction:
   ```text
   Sorry, the batch number is CHG260712A and affected quantity is 50 kg
   ```
2. Click **Send**.
3. **Show what happens**:
   - The AI Assistant understands the **edit intent** through the LangGraph classifier.
   - The **Batch/Lot Number** on the left form smoothly updates to `CHG260712A`.
   - All other existing form values are **strictly preserved**.
   - The **AI Copilot Risk Assessment** dynamically refreshes.

---

### Part 4: AI Tool 3 – Document Extraction (PDF / DOCX / TXT) (4:30 – 6:30)
1. Click **Reset Form** on the left to clear the form.
2. Demonstrate file upload by dragging or clicking to select:
   - `d:\assignment\sample_documents\deviation_metformin_oos.pdf`
   - (Or try `deviation_email_incident.txt` or `deviation_batch_excursion.docx`!)
3. **Show what happens**:
   - The file parser extracts raw text from the PDF/DOCX.
   - The LangGraph extraction node maps all fields into structured Pydantic schemas.
   - The left form instantly populates with full batch and incident data.
   - The AI Copilot Risk Assessment generates context-specific pharma recommendations.
4. Demonstrate that the user can still review and edit any field directly if they want human oversight.

---

### Part 5: Save Deviation & Database Persistence (6:30 – 7:30)
1. Click **Save Deviation** (blue button with floppy disk icon).
2. A green floating toast confirms: *"Deviation DEV-YYYYMMDD-XXXXXX saved successfully!"*
3. Click the **Records** button in the top navigation bar.
4. Show the **Saved Deviation Records** modal displaying the persisted records from the SQLite database.

---

### Part 6: Technical Architecture Code Walkthrough (7:30 – 10:00)
Walk through the codebase briefly:
- **Frontend Architecture (`frontend/src/`)**:
  - `store/deviationSlice.js`: Redux Toolkit slice managing single source of truth for form fields, risk assessments, and async thunks (`processTextPrompt`, `processDocument`, `saveDeviation`).
  - `components/LogDeviationForm.jsx`: Controlled component bound to Redux state.
  - `components/AIDeviationAssistant.jsx`: Multimodal input hub (drag & drop, text paste, conversational prompt).
- **Backend Architecture (`backend/`)**:
  - `main.py`: FastAPI application exposing `/api/process-text`, `/api/process-document`, `/api/save-deviation`.
  - `graph.py`: LangGraph `StateGraph` with intent classification (`log`, `edit`, `document`), field extraction, and risk assessment nodes.
  - `file_parser.py`: Multi-format text extraction (PyMuPDF for PDF, python-docx for Word, openpyxl for Excel).
  - `database.py` & `models.py`: Async SQLAlchemy engine with SQLite/PostgreSQL support.
