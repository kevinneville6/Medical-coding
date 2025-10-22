from fastapi import FastAPI
from pydantic import BaseModel
import os
from typing import Dict, List

app = FastAPI(
    title="Medical Coding API",
    description="AI-powered medical coding assistance",
    version="1.0.0"
)

class PatientDescription(BaseModel):
    patient_description: str

class CodingResponse(BaseModel):
    status: str
    report_id: str
    suggested_codes: List[str]
    confidence: float
    reasoning: str

@app.get("/")
def root():
    return {
        "service": "Medical Coding API", 
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "medical-coding-api"}

@app.post("/analyze", response_model=CodingResponse)
def analyze(description: PatientDescription):
    # Basic medical coding logic - expand this with your actual logic
    patient_text = description.patient_description.lower()
    
    # Simple keyword-based coding (replace with your ML model)
    suggested_codes = []
    reasoning = []
    
    if "fever" in patient_text and "cough" in patient_text:
        suggested_codes.extend(["R50.9", "R05"])
        reasoning.append("Fever and cough symptoms detected")
    
    if "headache" in patient_text:
        suggested_codes.append("R51")
        reasoning.append("Headache symptom detected")
        
    if "hypertension" in patient_text:
        suggested_codes.append("I10")
        reasoning.append("Hypertension condition identified")
    
    # If no specific codes found, provide general codes
    if not suggested_codes:
        suggested_codes = ["R69"]  # Illness, unspecified
        reasoning.append("General symptoms detected")
    
    return {
        "status": "success",
        "report_id": f"report_{len(patient_text)}",
        "suggested_codes": suggested_codes,
        "confidence": 0.85,
        "reasoning": "; ".join(reasoning)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
