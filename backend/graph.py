"""
graph.py – LangGraph StateGraph for the AI Deviation Assistant.

Three tools implemented as graph nodes:
  1. log_deviation   – Extract form fields from a text prompt (new deviation)
  2. edit_deviation  – Update specific fields based on correction prompt
  3. document_extract – Extract from uploaded document text

Workflow:
  START → classify_intent → (branch) → extract/edit → assess_risk → END
"""
import json
import logging
import re
from typing import TypedDict, Optional, Annotated
import operator

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START

from database import settings

logger = logging.getLogger(__name__)

# ── LLM instance ─────────────────────────────────────────────────────────────
def get_llm(temperature: float = 0.1) -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.GROQ_API_KEY,
        temperature=temperature,
        max_tokens=2048,
    )


# ── State definition ──────────────────────────────────────────────────────────
class DeviationState(TypedDict):
    raw_input: str                    # text from user (prompt or extracted doc text)
    intent: str                       # "log" | "edit" | "document"
    current_form: dict                # existing form fields (for edit mode)
    form_fields: dict                 # extracted / updated form fields
    risk_assessment: dict             # AI-generated risk assessment
    ai_message: str                   # human-readable summary from AI
    messages: Annotated[list, operator.add]  # conversation history


# ── Helper: strip markdown code fences and parse JSON ────────────────────────
def _parse_json_from_response(text: str) -> dict:
    """
    Extract JSON from an LLM response that may include markdown code fences
    or extra commentary.
    """
    # Try to find ```json ... ``` block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        text = match.group(1)
    # Try to find the first { ... } block
    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        text = brace_match.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Could not parse JSON from LLM response: %s", text[:200])
        return {}


# ── Node: classify intent ─────────────────────────────────────────────────────
def classify_intent(state: DeviationState) -> DeviationState:
    """
    Determines whether the user wants to:
      - "log"      : report a new deviation from scratch
      - "edit"     : correct/update fields of an existing deviation
      - "document" : the input is extracted from an uploaded document
    """
    if state["intent"] == "document":
        # Already set by the API layer when a file was uploaded
        return state

    llm = get_llm()
    prompt = f"""You are an intent classifier for a pharmaceutical Deviation Management system.

User message: "{state['raw_input']}"

Classify the intent as EXACTLY one of:
- "log"  : The user is reporting a new deviation event (process parameter out of range, OOS result, equipment failure, contamination, missing SOP step, etc.)
- "edit" : The user is correcting or adding information to an already-reported deviation (e.g., "sorry, the batch number is X", "the affected quantity is Y")

Reply with ONLY the word: log  OR  edit"""

    response = llm.invoke([HumanMessage(content=prompt)])
    intent_raw = response.content.strip().lower()
    intent = "edit" if "edit" in intent_raw else "log"
    return {**state, "intent": intent}


# ── Node: extract deviation fields from text ──────────────────────────────────
def extract_deviation(state: DeviationState) -> DeviationState:
    """
    Extracts all Log Deviation form fields from raw text.
    Used for both "log" and "document" intents.
    """
    llm = get_llm()

    system_prompt = """You are an expert pharmaceutical Quality Assurance specialist working for an API (Active Pharmaceutical Ingredient) manufacturer.
Your task is to extract deviation information from text and return it as structured JSON.

ALLOWED VALUES for dropdowns:
- site_plant: "API Manufacturing Unit" | "R&D Lab" | "QC Lab" | "Warehouse" | "Packaging Unit"
- source: "Manufacturing" | "QC Lab" | "Warehouse" | "Customer Complaint" | "Audit" | "Self-Inspection"
- initial_impact: "No Impact" | "Minor" | "Moderate" | "Major" | "Critical"
- initial_severity: "Low" | "Medium" | "High" | "Critical"

IMPORTANT: For date_of_occurrence, use format dd-mm-yyyy. If not specified, use null.

Return ONLY valid JSON matching this structure (use null for missing fields):
{
  "site_plant": "...",
  "date_of_occurrence": "dd-mm-yyyy or null",
  "title": "concise title (max 80 chars)",
  "source": "...",
  "related_product": "...",
  "batch_lot_number": "...",
  "detailed_description": "comprehensive description (what happened, where, when, how detected)",
  "initial_impact": "...",
  "initial_severity": "..."
}"""

    user_prompt = f"""Extract the deviation information from this text:

{state['raw_input']}"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    fields = _parse_json_from_response(response.content)
    return {**state, "form_fields": fields}


# ── Node: edit/update specific fields ────────────────────────────────────────
def edit_deviation(state: DeviationState) -> DeviationState:
    """
    Updates only the fields mentioned in the user's correction prompt,
    preserving all other existing form field values.
    """
    llm = get_llm()

    current = state.get("current_form", {})

    system_prompt = """You are an expert pharmaceutical QA specialist.
The user wants to CORRECT or ADD specific fields to an existing deviation report.
Extract ONLY the fields they are changing/adding. Leave all other fields unchanged.

ALLOWED VALUES:
- site_plant: "API Manufacturing Unit" | "R&D Lab" | "QC Lab" | "Warehouse" | "Packaging Unit"
- source: "Manufacturing" | "QC Lab" | "Warehouse" | "Customer Complaint" | "Audit" | "Self-Inspection"
- initial_impact: "No Impact" | "Minor" | "Moderate" | "Major" | "Critical"
- initial_severity: "Low" | "Medium" | "High" | "Critical"

Return ONLY valid JSON with the fields to update (omit fields that are NOT being changed):
{
  "batch_lot_number": "new value if changed",
  "related_product": "new value if changed",
  ...
}"""

    user_prompt = f"""Current deviation form:
{json.dumps(current, indent=2)}

User correction: "{state['raw_input']}"

Return ONLY the JSON object containing fields to update."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    updates = _parse_json_from_response(response.content)
    # Merge: current fields + updates (updates take priority)
    merged = {**current, **{k: v for k, v in updates.items() if v is not None}}
    return {**state, "form_fields": merged}


# ── Node: generate AI risk assessment ────────────────────────────────────────
def assess_risk(state: DeviationState) -> DeviationState:
    """
    Generates the AI Deviation Assistant risk assessment panel content
    based on the extracted form fields.
    """
    llm = get_llm(temperature=0.3)
    fields = state.get("form_fields", {})

    system_prompt = """You are a senior pharmaceutical QA risk assessor specializing in API manufacturing.
Based on the deviation information provided, generate a risk assessment.

Return ONLY valid JSON:
{
  "severity_classification": "Minor | Moderate | Major | Critical",
  "impact_assessment": "1-2 sentences on product/patient/regulatory impact",
  "suggested_next_action": "specific recommended actions (max 3 bullet points as plain text)",
  "risk_reasoning": "2-3 sentence explanation of your assessment reasoning",
  "regulatory_risk": "Yes | No"
}"""

    user_prompt = f"""Deviation details:
Title: {fields.get('title', 'N/A')}
Product: {fields.get('related_product', 'N/A')}
Batch: {fields.get('batch_lot_number', 'N/A')}
Site: {fields.get('site_plant', 'N/A')}
Source: {fields.get('source', 'N/A')}
Impact: {fields.get('initial_impact', 'N/A')}
Severity: {fields.get('initial_severity', 'N/A')}
Description: {fields.get('detailed_description', 'N/A')}

Generate the risk assessment."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    risk = _parse_json_from_response(response.content)

    # Generate a friendly AI message summarizing what was done
    intent = state.get("intent", "log")
    if intent == "edit":
        ai_msg = (
            f"✅ I've updated the deviation form with your corrections. "
            f"The risk assessment has been refreshed based on the latest information."
        )
    elif intent == "document":
        ai_msg = (
            f"✅ I've extracted the deviation details from your document and populated the form. "
            f"Please review the extracted information and make any corrections if needed."
        )
    else:
        title = fields.get("title", "the reported deviation")
        severity = risk.get("severity_classification", "unknown")
        ai_msg = (
            f"✅ I've analyzed your input and populated the deviation form. "
            f"The event has been classified as **{severity}** severity. "
            f"Please review all fields and adjust any details before saving."
        )

    return {**state, "risk_assessment": risk, "ai_message": ai_msg}


# ── Build the graph ───────────────────────────────────────────────────────────
def _route_intent(state: DeviationState) -> str:
    """Conditional edge: route to extract or edit node based on intent."""
    return state.get("intent", "log")


def build_deviation_graph():
    """Compile and return the LangGraph StateGraph."""
    graph = StateGraph(DeviationState)

    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("extract_deviation", extract_deviation)
    graph.add_node("edit_deviation", edit_deviation)
    graph.add_node("assess_risk", assess_risk)

    # Edges
    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        _route_intent,
        {
            "log": "extract_deviation",
            "edit": "edit_deviation",
            "document": "extract_deviation",
        },
    )
    graph.add_edge("extract_deviation", "assess_risk")
    graph.add_edge("edit_deviation", "assess_risk")
    graph.add_edge("assess_risk", END)

    return graph.compile()


# Singleton compiled graph (imported by main.py)
deviation_graph = build_deviation_graph()
