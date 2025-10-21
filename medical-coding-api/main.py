from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
import uuid
import logging
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Medical Coding API",
    description="AI-powered medical coding analysis using Kimi AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and Response Models - Pydantic v1 compatible
class CodingRequest(BaseModel):
    patient_description: str
    max_cpt_codes: Optional[int] = 8
    max_icd_codes: Optional[int] = 8
    max_hcpcs_codes: Optional[int] = 6
    structured_context: Optional[str] = None

class CodingResponse(BaseModel):
    report_id: str
    status: str
    model: str
    response_id: Optional[str] = None
    agent_warnings: List[str] = []
    agent_metadata: Optional[Dict[str, Any]] = None
    tool_calls: List[str] = []
    raw_agent_output: Dict[str, Any]
    input: Optional[Dict[str, Any]] = None
    prompt_variables: Optional[Dict[str, Any]] = None
    configuration_snapshot: Optional[Dict[str, Any]] = None

# Mock medical coding agent
class MedicalCodingAgent:
    def __init__(self):
        self.model_name = "kimi-k2-0905-preview"
        self.use_web_search = True
        
    def analyze(self, patient_description: str, max_codes: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Mock analysis function - replace this with your actual medical coding agent
        """
        try:
            report_id = f"report-{uuid.uuid4().hex[:8]}"
            response_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
            
            analysis_result = self._keyword_analysis(patient_description)
            
            return {
                "report_id": report_id,
                "status": "success",
                "model": self.model_name,
                "response_id": response_id,
                "agent_warnings": [],
                "agent_metadata": {
                    "request_timeout": 300.0,
                    "use_web_search": self.use_web_search,
                    "usage": {
                        "completion_tokens": 1200,
                        "prompt_tokens": 800,
                        "total_tokens": 2000,
                    },
                    "model": self.model_name,
                    "finish_reason": "stop",
                    "tool_iterations": 0
                },
                "tool_calls": [],
                "raw_agent_output": analysis_result,
                "input": {
                    "content_hash": uuid.uuid4().hex,
                    "structured_input": True,
                    "character_count": len(patient_description)
                },
                "prompt_variables": {
                    "report_id": report_id,
                    "content_hash": uuid.uuid4().hex,
                    "structured_context": "Structured medical coding analysis",
                    "report_text": patient_description,
                    "max_cpt_codes": max_codes.get('cpt', 8) if max_codes else 8,
                    "max_icd_codes": max_codes.get('icd', 8) if max_codes else 8,
                    "max_hcpcs_codes": max_codes.get('hcpcs', 6) if max_codes else 6
                },
                "configuration_snapshot": {
                    "model": {
                        "provider": "kimi",
                        "name": self.model_name,
                        "temperature": 0.2,
                        "max_input_tokens": 8096,
                    },
                    "agent": {
                        "offline_mode": False,
                        "poll_interval": 1.5,
                        "request_timeout": 300.0,
                        "max_output_tokens": 2048,
                        "use_web_search": self.use_web_search,
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Agent analysis failed: {str(e)}")
            raise

    def _keyword_analysis(self, patient_description: str) -> Dict[str, Any]:
        description_lower = patient_description.lower()
        
        if any(keyword in description_lower for keyword in ['appendectomy', 'appendicitis', 'rlq pain']):
            return {
                "report_summary": "Patient presents with signs suggestive of acute appendicitis. Analysis indicates need for emergency department evaluation and potential surgical intervention.",
                "cpt_codes": [
                    {
                        "code": "99283",
                        "description": "Emergency department visit, low severity, requiring urgent evaluation.",
                        "modifiers": [],
                        "confidence": 0.85,
                        "rationale": "Clinical picture meets 2025 ED low-moderate MDM per CPT guidelines.",
                        "flags": [],
                        "web_sources": ["https://www.ama-assn.org/practice-management/cpt/cpt-ed-e-m-codes-2025"]
                    },
                    {
                        "code": "44970",
                        "description": "Laparoscopy, surgical, appendectomy.",
                        "modifiers": [],
                        "confidence": 0.75,
                        "rationale": "Documented plan for laparoscopic appendectomy.",
                        "flags": ["CONFIRMATION_NEEDED"],
                        "web_sources": ["https://www.ama-assn.org/practice-management/cpt/cpt-appendectomy-codes"]
                    }
                ],
                "icd10_codes": [
                    {
                        "code": "K35.9",
                        "description": "Acute appendicitis, unspecified.",
                        "confidence": 0.80,
                        "rationale": "Clinical presentation consistent with acute appendicitis.",
                        "flags": [],
                        "web_sources": ["https://www.cms.gov/icd10m/2025-Icd-10-CM"]
                    },
                    {
                        "code": "R10.31",
                        "description": "Right lower-quadrant pain.",
                        "confidence": 0.90,
                        "rationale": "Chief complaint localized to RLQ.",
                        "flags": [],
                        "web_sources": []
                    }
                ],
                "hcpcs_codes": [
                    {
                        "code": "J0696",
                        "description": "Injection, ceftriaxone sodium, per 250 mg.",
                        "confidence": 0.60,
                        "rationale": "Common empiric antibiotic for appendicitis.",
                        "flags": ["CONFIRMATION_NEEDED"],
                        "web_sources": ["https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleId=52428"]
                    }
                ],
                "medical_necessity": {
                    "validated": True,
                    "comments": "ED visit and potential surgical intervention medically necessary for suspected acute appendicitis."
                },
                "overall_confidence": 0.78,
                "flags": ["CONFIRMATION_NEEDED"],
                "recommendations": [
                    "Confirm operative report availability for appendectomy",
                    "Document specific antibiotic administration details",
                    "Provide imaging results if available"
                ],
                "search_queries": [
                    "acute appendicitis ICD-10 2025",
                    "laparoscopic appendectomy CPT",
                    "ED visit coding guidelines 2025"
                ]
            }
        else:
            return {
                "report_summary": f"Analysis of patient case: {patient_description[:100]}...",
                "cpt_codes": [
                    {
                        "code": "99213",
                        "description": "Office/outpatient visit, established patient.",
                        "modifiers": [],
                        "confidence": 0.70,
                        "rationale": "Routine evaluation and management service.",
                        "flags": [],
                        "web_sources": ["CPT-AMA"]
                    }
                ],
                "icd10_codes": [
                    {
                        "code": "Z00.00",
                        "description": "Encounter for general adult medical examination.",
                        "confidence": 0.65,
                        "rationale": "General medical examination documented.",
                        "flags": [],
                        "web_sources": ["ICD10Data.com"]
                    }
                ],
                "hcpcs_codes": [],
                "medical_necessity": {
                    "validated": True,
                    "comments": "Services appear medically necessary based on available documentation."
                },
                "overall_confidence": 0.65,
                "flags": ["GENERAL_ANALYSIS"],
                "recommendations": [
                    "Provide more specific clinical details for accurate coding",
                    "Include duration and severity of symptoms",
                    "Specify any diagnostic test results"
                ],
                "search_queries": [
                    "office visit CPT coding",
                    "general exam ICD-10"
                ]
            }

medical_agent = MedicalCodingAgent()

@app.get("/")
async def root():
    return {
        "message": "Medical Coding API is running", 
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/analyze", response_model=CodingResponse)
async def analyze_medical_case(request: CodingRequest):
    try:
        logger.info(f"Received analysis request: {len(request.patient_description)} characters")
        
        if not request.patient_description.strip():
            raise HTTPException(status_code=400, detail="Patient description is required")
        
        if len(request.patient_description) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Patient description too short (minimum 10 characters required)"
            )
        
        if len(request.patient_description) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Patient description too long (maximum 10,000 characters)"
            )

        max_codes = {
            'cpt': request.max_cpt_codes,
            'icd': request.max_icd_codes,
            'hcpcs': request.max_hcpcs_codes
        }

        result = medical_agent.analyze(
            patient_description=request.patient_description,
            max_codes=max_codes
        )
        
        logger.info(f"Analysis completed: {result['report_id']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error during analysis: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "medical-coding-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/info")
async def api_info():
    return {
        "name": "Medical Coding API",
        "version": "1.0.0",
        "description": "AI-powered medical coding analysis",
        "endpoints": {
            "POST /analyze": "Analyze patient descriptions for medical coding",
            "GET /health": "Health check",
            "GET /info": "API information"
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
