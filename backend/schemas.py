"""
schemas.py – Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Form fields the AI can populate ─────────────────────────────────────────

class DeviationFormFields(BaseModel):
    """All fields that appear in the Log Deviation form."""
    site_plant: Optional[str] = None
    date_of_occurrence: Optional[str] = None          # ISO date string dd-mm-yyyy
    title: Optional[str] = None
    source: Optional[str] = None
    related_product: Optional[str] = None
    batch_lot_number: Optional[str] = None
    detailed_description: Optional[str] = None
    initial_impact: Optional[str] = None              # Minor / Moderate / Major / Critical
    initial_severity: Optional[str] = None            # Low / Medium / High / Critical


class AIRiskAssessment(BaseModel):
    """AI-generated risk assessment panel."""
    severity_classification: Optional[str] = None
    impact_assessment: Optional[str] = None
    suggested_next_action: Optional[str] = None
    risk_reasoning: Optional[str] = None
    regulatory_risk: Optional[str] = None             # "Yes" | "No"


# ── Requests ─────────────────────────────────────────────────────────────────

class TextProcessRequest(BaseModel):
    """Sent by the frontend when the user types a prompt."""
    message: str = Field(..., min_length=1)
    current_form: Optional[DeviationFormFields] = None  # existing form state for edit mode


# ── Responses ────────────────────────────────────────────────────────────────

class ProcessResponse(BaseModel):
    """Returned after any AI processing (text or document)."""
    intent: str                        # "log" | "edit" | "document"
    form_fields: DeviationFormFields
    risk_assessment: AIRiskAssessment
    ai_message: str                    # Human-readable explanation from AI
    confidence: float = 0.9


class SaveDeviationRequest(BaseModel):
    """Payload when the user clicks Save Deviation."""
    form_fields: DeviationFormFields
    risk_assessment: AIRiskAssessment


class SaveDeviationResponse(BaseModel):
    deviation_id: str
    status: str
    message: str


class DeviationRecord(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    site_plant: Optional[str]
    date_of_occurrence: Optional[str]
    title: Optional[str]
    source: Optional[str]
    related_product: Optional[str]
    batch_lot_number: Optional[str]
    detailed_description: Optional[str]
    initial_impact: Optional[str]
    initial_severity: Optional[str]
    ai_severity_classification: Optional[str]
    ai_impact_assessment: Optional[str]
    ai_suggested_next_action: Optional[str]
    ai_risk_reasoning: Optional[str]
    ai_regulatory_risk: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
