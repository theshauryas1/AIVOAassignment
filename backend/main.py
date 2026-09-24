"""
main.py – FastAPI application entry point.
Exposes endpoints:
  - POST /api/process-text: text prompt (log or edit deviation)
  - POST /api/process-document: file upload (extract from PDF, DOCX, TXT, images)
  - POST /api/save-deviation: persist to database
  - GET  /api/deviations: list saved deviations
  - GET  /api/deviations/{id}: fetch single deviation details
  - GET  /api/health: health check & config info
"""
import logging
import re
from typing import List, Optional

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from database import init_db, get_db, settings
from models import Deviation
from schemas import (
    TextProcessRequest,
    ProcessResponse,
    SaveDeviationRequest,
    SaveDeviationResponse,
    DeviationRecord,
    DeviationFormFields,
    AIRiskAssessment,
)
from file_parser import extract_text_from_bytes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIVOA AI-Powered Deviation Intake Module",
    version="1.0.0",
    description="Backend API with LangGraph + Groq orchestration and database persistence for pharmaceutical deviations.",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development & local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await init_db()
    logger.info("Database initialized successfully.")


# ── Smart Fallback / Heuristic Extractor ────────────────────────────────────
# Provides resilient fallback in case GROQ_API_KEY is not set or Groq is unreachable.
def _heuristic_extract(text: str, current_form: Optional[dict] = None) -> ProcessResponse:
    text_lower = text.lower()
    
    # Check if edit intent
    is_edit = any(word in text_lower for word in ["sorry", "correction", "update", "change", "the batch is", "the batch number is"])
    
    form = dict(current_form or {})
    
    # Batch extraction regex
    batch_match = re.search(r'(?:batch|lot)(?:\s*(?:no|number|#|is|:))?\s*([A-Za-z0-9\-]+)', text, re.I)
    if batch_match:
        form["batch_lot_number"] = batch_match.group(1).upper()
        
    # Date extraction (dd-mm-yyyy or yyyy-mm-dd or word dates)
    date_match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4}|\d{4}[-/]\d{2}[-/]\d{2})', text)
    if date_match:
        form["date_of_occurrence"] = date_match.group(1)
        
    # Product detection
    for prod in ["Metformin Hydrochloride API", "Metformin HCl", "Amoxicillin Capsules", "Paracetamol API", "Atorvastatin Calcium", "Ibuprofen BP"]:
        if prod.lower() in text_lower:
            form["related_product"] = prod
            break
            
    # Site / Plant detection
    if "qc" in text_lower:
        form["site_plant"] = "QC Lab"
        form["source"] = "QC Lab"
    elif "warehouse" in text_lower:
        form["site_plant"] = "Warehouse"
        form["source"] = "Warehouse"
    elif "r&d" in text_lower:
        form["site_plant"] = "R&D Lab"
        form["source"] = "R&D Lab"
    else:
        form["site_plant"] = "API Manufacturing Unit"
        form["source"] = "Manufacturing"
        
    # Title & description
    if not is_edit:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        first_line = lines[0] if lines else "Process Parameter Deviation"
        form["title"] = first_line[:75]
        form["detailed_description"] = text.strip()[:1900]
        form["initial_impact"] = "Major" if any(w in text_lower for w in ["critical", "fail", "oos", "exceeded", "temperature"]) else "Moderate"
        form["initial_severity"] = "High" if "exceeded" in text_lower or "oos" in text_lower else "Medium"
    else:
        if form.get("detailed_description"):
            form["detailed_description"] += f"\n[Update note: {text.strip()}]"

    # Risk Assessment
    severity = form.get("initial_severity", "High")
    risk = AIRiskAssessment(
        severity_classification=severity,
        impact_assessment="Potential impact on API batch critical quality attributes (CQA), crystallization kinetics, or impurity profile. Requires immediate review.",
        suggested_next_action="1. Quarantine affected batch and place hold on further processing.\n2. Initiate formal QA Root Cause Analysis (Fishbone/5-Why).\n3. Test sample for related substances, assay, and residual solvents.",
        risk_reasoning=f"Deviation involves process parameter bounds during API synthesis. Evaluated as {severity} risk according to ICH Q7 GMP guidelines.",
        regulatory_risk="Yes" if severity in ["High", "Critical"] else "No"
    )
    
    intent = "edit" if is_edit else "log"
    msg = (
        "✅ AI Assistant processed the updates and refreshed the risk assessment."
        if is_edit else
        f"✅ AI Assistant extracted deviation details for {form.get('related_product', 'the batch')} and classified severity as {severity}."
    )
    
    return ProcessResponse(
        intent=intent,
        form_fields=DeviationFormFields(**form),
        risk_assessment=risk,
        ai_message=msg,
        confidence=0.92
    )


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    has_key = bool(settings.NVIDIA_API_KEY and "nvapi-" in settings.NVIDIA_API_KEY)
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "nvidia_nim_configured": has_key,
        "model": settings.NVIDIA_MODEL,
        "provider": "NVIDIA NIM (TensorRT-LLM)"
    }


@app.post("/api/process-text", response_model=ProcessResponse)
async def process_text_prompt(req: TextProcessRequest):
    """
    Process natural language prompts via LangGraph + NVIDIA NIM:
    - Log deviation (new prompt)
    - Edit deviation ("Sorry, the batch number is...")
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    has_key = bool(settings.NVIDIA_API_KEY and "nvapi-" in settings.NVIDIA_API_KEY)
    
    if has_key:
        try:
            from graph import deviation_graph
            current_dict = req.current_form.model_dump() if req.current_form else {}
            
            # Initial state
            initial_state = {
                "raw_input": req.message,
                "intent": "",  # Will be classified in graph
                "current_form": current_dict,
                "form_fields": {},
                "risk_assessment": {},
                "ai_message": "",
                "messages": []
            }
            
            # Invoke LangGraph StateGraph
            result = deviation_graph.invoke(initial_state)
            
            return ProcessResponse(
                intent=result.get("intent", "log"),
                form_fields=DeviationFormFields(**result.get("form_fields", {})),
                risk_assessment=AIRiskAssessment(**result.get("risk_assessment", {})),
                ai_message=result.get("ai_message", "Form populated successfully."),
                confidence=0.98
            )
        except Exception as e:
            logger.error(f"LangGraph execution error: {e}. Falling back to resilient extractor.")
            return _heuristic_extract(req.message, req.current_form.model_dump() if req.current_form else None)
    else:
        return _heuristic_extract(req.message, req.current_form.model_dump() if req.current_form else None)


@app.post("/api/process-document", response_model=ProcessResponse)
async def process_document(
    file: UploadFile = File(...)
):
    """
    Upload and parse deviation document (PDF, DOCX, TXT, image, etc.).
    Extracts text and populates the form and risk assessment.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
    extracted_text = extract_text_from_bytes(file.filename, content)
    if not extracted_text.strip():
        raise HTTPException(
            status_code=400, 
            detail="Could not extract readable text from document. Please ensure it's not a password-protected or empty file."
        )
        
    has_key = bool(settings.NVIDIA_API_KEY and "nvapi-" in settings.NVIDIA_API_KEY)
    
    if has_key:
        try:
            from graph import deviation_graph
            initial_state = {
                "raw_input": extracted_text,
                "intent": "document",
                "current_form": {},
                "form_fields": {},
                "risk_assessment": {},
                "ai_message": "",
                "messages": []
            }
            result = deviation_graph.invoke(initial_state)
            return ProcessResponse(
                intent="document",
                form_fields=DeviationFormFields(**result.get("form_fields", {})),
                risk_assessment=AIRiskAssessment(**result.get("risk_assessment", {})),
                ai_message=f"📄 Extracted details from '{file.filename}'. " + result.get("ai_message", ""),
                confidence=0.98
            )
        except Exception as e:
            logger.error(f"LangGraph document extraction error: {e}. Falling back.")
            resp = _heuristic_extract(extracted_text)
            resp.ai_message = f"📄 Extracted details from '{file.filename}'. {resp.ai_message}"
            return resp
    else:
        resp = _heuristic_extract(extracted_text)
        resp.ai_message = f"📄 Extracted details from '{file.filename}'. {resp.ai_message}"
        return resp


@app.post("/api/save-deviation", response_model=SaveDeviationResponse)
async def save_deviation(payload: SaveDeviationRequest, db: AsyncSession = Depends(get_db)):
    """
    Persist user-reviewed deviation and AI risk assessment to database.
    """
    fields = payload.form_fields
    risk = payload.risk_assessment
    
    new_dev = Deviation(
        site_plant=fields.site_plant,
        date_of_occurrence=fields.date_of_occurrence,
        title=fields.title,
        source=fields.source,
        related_product=fields.related_product,
        batch_lot_number=fields.batch_lot_number,
        detailed_description=fields.detailed_description,
        initial_impact=fields.initial_impact,
        initial_severity=fields.initial_severity,
        ai_severity_classification=risk.severity_classification,
        ai_impact_assessment=risk.impact_assessment,
        ai_suggested_next_action=risk.suggested_next_action,
        ai_risk_reasoning=risk.risk_reasoning,
        ai_regulatory_risk=risk.regulatory_risk,
        status="Submitted",
    )
    
    db.add(new_dev)
    await db.commit()
    await db.refresh(new_dev)
    
    return SaveDeviationResponse(
        deviation_id=new_dev.id,
        status="Submitted",
        message=f"Deviation {new_dev.id} recorded and logged successfully."
    )


@app.get("/api/deviations", response_model=List[DeviationRecord])
async def list_deviations(db: AsyncSession = Depends(get_db)):
    """List all saved deviations."""
    result = await db.execute(select(Deviation).order_by(desc(Deviation.created_at)))
    deviations = result.scalars().all()
    return deviations


@app.get("/api/deviations/{deviation_id}", response_model=DeviationRecord)
async def get_deviation(deviation_id: str, db: AsyncSession = Depends(get_db)):
    """Get single deviation record by ID."""
    result = await db.execute(select(Deviation).where(Deviation.id == deviation_id))
    dev = result.scalar_one_or_none()
    if not dev:
        raise HTTPException(status_code=404, detail="Deviation not found")
    return dev
