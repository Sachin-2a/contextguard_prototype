from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from deterministic import detect_structured_ids
from ner import detect_entities
from llm_context import analyze_context
from policy import apply_policy
from vault import log_audit, substitute_tokens

app = FastAPI(title="ContextGuard Gateway")

class RequestEnvelope(BaseModel):
    text: str
    requester_role: str
    data_source: str
    destination: str
    purpose: str

@app.post("/process")
async def process_text(req: RequestEnvelope):
    context = {
        "requester_role": req.requester_role,
        "data_source": req.data_source,
        "destination": req.destination,
        "purpose": req.purpose
    } #[cite: 4]

    # Layer 1: Deterministic (Regex + Checksums)[cite: 4]
    hard_hits = detect_structured_ids(req.text)
    
    # Layer 2: NER (Presidio)[cite: 4]
    ner_hits = detect_entities(req.text)
    
    # Layer 3: Contextual LLM[cite: 4]
    llm_analysis = analyze_context(req.text, context)
    
    all_findings = hard_hits + ner_hits + llm_analysis.get("findings", [])

    # Policy Engine & Vault handling[cite: 4]
    final_text, actions_taken = apply_policy(req.text, all_findings, context)
    
    log_audit(req.text, final_text, actions_taken, context) #[cite: 4]

    return {
        "original_text": req.text,
        "secured_text": final_text,
        "actions": actions_taken,
        "llm_reasoning": llm_analysis.get("reason", "Standard policy applied.")
    }
