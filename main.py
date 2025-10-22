from fastapi import FastAPI
from pydantic import BaseModel
import os
import re
from typing import Dict, List, Optional

app = FastAPI(
    title="Medical Coding API",
    description="AI-powered medical coding assistance with ICD-10 codes",
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
    additional_notes: Optional[str] = None

# Enhanced ICD-10 code database
MEDICAL_CODES = {
    "fever": ["R50.9", "Fever, unspecified"],
    "cough": ["R05", "Cough"],
    "headache": ["R51", "Headache"],
    "hypertension": ["I10", "Essential (primary) hypertension"],
    "diabetes": ["E11.9", "Type 2 diabetes mellitus without complications"],
    "chest_pain": ["R07.9", "Chest pain, unspecified"],
    "shortness_of_breath": ["R06.02", "Shortness of breath"],
    "nausea": ["R11.0", "Nausea"],
    "vomiting": ["R11.10", "Vomiting, unspecified"],
    "abdominal_pain": ["R10.9", "Unspecified abdominal pain"],
    "fatigue": ["R53.83", "Other fatigue"],
    "dizziness": ["R42", "Dizziness and giddiness"],
    "back_pain": ["M54.9", "Dorsalgia, unspecified"],
    "urinary_tract_infection": ["N39.0", "Urinary tract infection, site not specified"],
    "pneumonia": ["J18.9", "Pneumonia, unspecified organism"],
    "asthma": ["J45.909", "Unspecified asthma, uncomplicated"],
    "copd": ["J44.9", "COPD, unspecified"],
    "myocardial_infarction": ["I21.9", "Acute myocardial infarction, unspecified"],
    "stroke": ["I63.9", "Cerebral infarction, unspecified"],
    "anxiety": ["F41.9", "Anxiety disorder, unspecified"],
    "depression": ["F32.9", "Major depressive disorder, single episode, unspecified"]
}

def analyze_medical_text(text: str):
    """Enhanced medical text analysis with pattern matching"""
    text_lower = text.lower()
    found_conditions = []
    reasoning = []
    
    # Check for each condition
    for condition, (code, description) in MEDICAL_CODES.items():
        condition_phrase = condition.replace('_', ' ')
        if condition_phrase in text_lower:
            found_conditions.append(code)
            reasoning.append(description)
    
    # Special pattern matching for combined symptoms
    if "fever" in text_lower and "cough" in text_lower:
        if "J18.9" not in found_conditions:  # Avoid duplicates
            found_conditions.append("J18.9")
            reasoning.append("Respiratory infection symptoms")
    
    if "chest pain" in text_lower and "shortness of breath" in text_lower:
        found_conditions.extend(["R07.9", "R06.02"])
        reasoning.append("Cardiac-related symptoms detected")
    
    # Calculate confidence based on matches
    confidence = min(0.3 + (len(found_conditions) * 0.15), 0.95)
    
    # Default code if nothing found
    if not found_conditions:
        found_conditions = ["R69"]  # Illness, unspecified
        reasoning = ["General symptoms detected - recommend further evaluation"]
        confidence = 0.3
    
    return found_conditions, confidence, reasoning

@app.get("/")
def root():
    return {
        "service": "Medical Coding API", 
        "status": "operational",
        "version": "1.0.0",
        "endpoints": ["/health", "/analyze", "/docs"],
        "total_codes_available": len(MEDICAL_CODES)
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "medical-coding-api"}

@app.get("/codes")
def list_codes():
    """Endpoint to see all available medical codes"""
    return {
        "total_codes": len(MEDICAL_CODES),
        "available_codes": MEDICAL_CODES
    }

@app.post("/analyze", response_model=CodingResponse)
def analyze(description: PatientDescription):
    try:
        patient_text = description.patient_description.strip()
        
        if not patient_text:
            return {
                "status": "error",
                "report_id": "error_001",
                "suggested_codes": [],
                "confidence": 0.0,
                "reasoning": "No patient description provided",
                "additional_notes": "Please provide a patient description for analysis"
            }
        
        # Analyze the medical text
        suggested_codes, confidence, reasoning_list = analyze_medical_text(patient_text)
        
        # Generate report ID
        report_id = f"report_{abs(hash(patient_text)) % 10000:04d}"
        
        response = {
            "status": "success",
            "report_id": report_id,
            "suggested_codes": suggested_codes,
            "confidence": round(confidence, 2),
            "reasoning": "; ".join(reasoning_list)
        }
        
        # Add notes for low confidence
        if confidence < 0.5:
            response["additional_notes"] = "Low confidence analysis - recommend manual review"
        
        return response
        
    except Exception as e:
        return {
            "status": "error",
            "report_id": "error_500",
            "suggested_codes": [],
            "confidence": 0.0,
            "reasoning": f"Analysis error: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
