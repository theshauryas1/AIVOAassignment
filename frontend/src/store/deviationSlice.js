import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const initialFormFields = {
  site_plant: 'API Manufacturing Unit',
  date_of_occurrence: '',
  title: '',
  source: '',
  related_product: '',
  batch_lot_number: '',
  detailed_description: '',
  initial_impact: '',
  initial_severity: '',
};

const initialRiskAssessment = {
  severity_classification: '',
  impact_assessment: '',
  suggested_next_action: '',
  risk_reasoning: '',
  regulatory_risk: '',
};

// ── Async Thunks ─────────────────────────────────────────────────────────────

export const processTextPrompt = createAsyncThunk(
  'deviation/processTextPrompt',
  async ({ message, currentForm }, { dispatch, rejectWithValue }) => {
    try {
      dispatch(setProgress({ progress: 25, message: 'Analyzing prompt and intent with AI...' }));
      
      const response = await fetch('/api/process-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, current_form: currentForm }),
      });

      dispatch(setProgress({ progress: 65, message: 'Extracting deviation fields & reasoning...' }));

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to process text prompt');
      }

      dispatch(setProgress({ progress: 95, message: 'Finalizing risk assessment...' }));
      const data = await response.json();
      
      setTimeout(() => {
        dispatch(setProgress({ progress: 100, message: 'Complete!' }));
      }, 200);

      return data;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const processDocument = createAsyncThunk(
  'deviation/processDocument',
  async (file, { dispatch, rejectWithValue }) => {
    try {
      dispatch(setProgress({ progress: 20, message: 'Reading document content and extracting text...' }));

      const formData = new FormData();
      formData.append('file', file);

      dispatch(setProgress({ progress: 45, message: 'Running AI extraction pipeline via LangGraph...' }));

      const response = await fetch('/api/process-document', {
        method: 'POST',
        body: formData,
      });

      dispatch(setProgress({ progress: 80, message: 'Structuring deviation data and risk assessment...' }));

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to process document');
      }

      const data = await response.json();
      dispatch(setProgress({ progress: 100, message: 'Document processed successfully!' }));
      return data;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const saveDeviation = createAsyncThunk(
  'deviation/saveDeviation',
  async ({ formFields, riskAssessment }, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/save-deviation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_fields: formFields,
          risk_assessment: riskAssessment,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save deviation');
      }

      return await response.json();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const fetchDeviations = createAsyncThunk(
  'deviation/fetchDeviations',
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/deviations');
      if (!response.ok) throw new Error('Failed to fetch deviations list');
      return await response.json();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

// ── Slice ────────────────────────────────────────────────────────────────────

const deviationSlice = createSlice({
  name: 'deviation',
  initialState: {
    formFields: { ...initialFormFields },
    riskAssessment: { ...initialRiskAssessment },
    status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
    error: null,
    progress: 0,
    progressMessage: '',
    aiMessage:
      'Upload a deviation report, lab result, or paste text above. I will automatically extract the relevant details and populate the form for you.',
    chatHistory: [],
    savedList: [],
    isSavedModalOpen: false,
    toast: null,
    formStatus: 'Draft',
  },
  reducers: {
    updateFormField: (state, action) => {
      const { field, value } = action.payload;
      state.formFields[field] = value;
    },
    resetForm: (state) => {
      state.formFields = { ...initialFormFields };
      state.riskAssessment = { ...initialRiskAssessment };
      state.progress = 0;
      state.progressMessage = '';
      state.formStatus = 'Draft';
      state.aiMessage =
        'Form has been reset. Upload a deviation document or enter a prompt to begin.';
    },
    setProgress: (state, action) => {
      state.progress = action.payload.progress;
      state.progressMessage = action.payload.message;
    },
    clearToast: (state) => {
      state.toast = null;
    },
    setSavedModalOpen: (state, action) => {
      state.isSavedModalOpen = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Process Text Prompt
      .addCase(processTextPrompt.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(processTextPrompt.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.formFields = { ...state.formFields, ...action.payload.form_fields };
        state.riskAssessment = action.payload.risk_assessment;
        state.aiMessage = action.payload.ai_message;
      })
      .addCase(processTextPrompt.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
        state.progress = 0;
      })

      // Process Document
      .addCase(processDocument.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(processDocument.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.formFields = { ...state.formFields, ...action.payload.form_fields };
        state.riskAssessment = action.payload.risk_assessment;
        state.aiMessage = action.payload.ai_message;
      })
      .addCase(processDocument.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
        state.progress = 0;
      })

      // Save Deviation
      .addCase(saveDeviation.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(saveDeviation.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.formStatus = 'Submitted';
        state.toast = `Deviation ${action.payload.deviation_id} saved successfully!`;
      })
      .addCase(saveDeviation.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })

      // Fetch Deviations
      .addCase(fetchDeviations.fulfilled, (state, action) => {
        state.savedList = action.payload;
      });
  },
});

export const { updateFormField, resetForm, setProgress, clearToast, setSavedModalOpen } =
  deviationSlice.actions;

export default deviationSlice.reducer;
