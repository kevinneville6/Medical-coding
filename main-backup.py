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

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Medical Coding API",
    description="AI-powered medical coding analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - configure for your webapp domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://your-webapp-domain.vercel.app",  # Your production webapp
        "*"  # Remove this in production and specify exact domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and Response Models
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

# Medical Coding Agent (Mock - Replace with your actual AI service)
class MedicalCodingAgent:
    def __init__(self):
        self.model_name = "kimi-medical-coder"
        self.use_web_search = True
        
    def analyze(self, patient_description: str, max_codes: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Mock medical coding analysis - Replace with actual AI integration
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
        """
        Mock analysis based on keywords - Replace with real AI service call
        """
        description_lower = patient_description.lower()
        
        # Appendicitis case
        if any(keyword in description_lower for keyword in ['appendectomy', 'appendicitis', 'rlq pain']):
            return self._appendicitis_analysis()
        # Diabetes case
        elif any(keyword in description_lower for keyword in ['diabetes', 'a1c', 'blood sugar']):
            return self._diabetes_analysis()
        # Hypertension case
        elif any(keyword in description_lower for keyword in ['hypertension', 'blood pressure', 'htn']):
            return self._hypertension_analysis()
        # General case
        else:
            return self._general_analysis(patient_description)

    def _appendicitis_analysis(self) -> Dict[str, Any]:
        return {
            "report_summary": "Patient presents with signs suggestive of acute appendicitis requiring surgical evaluation.",
            "cpt_codes": [
                {
                    "code": "99283",
                    "description": "Emergency department visit, low severity",
                    "modifiers": [],
                    "confidence": 0.85,
                    "rationale": "ED evaluation for acute abdominal pain",
                    "flags": [],
                    "web_sources": ["AMA CPT Guidelines 2025"]
                },
                {
                    "code": "44970",
                    "description": "Laparoscopy, surgical, appendectomy",
                    "modifiers": [],
                    "confidence": 0.75,
                    "rationale": "Laparoscopic appendectomy procedure",
                    "flags": ["CONFIRMATION_NEEDED"],
                    "web_sources": ["CPT Surgical Codes"]
                }
            ],
            "icd10_codes": [
                {
                    "code": "K35.9",
                    "description": "Acute appendicitis, unspecified",
                    "confidence": 0.80,
                    "rationale": "Primary diagnosis of acute appendicitis",
                    "flags": [],
                    "web_sources": ["ICD-10-CM 2025"]
                },
                {
                    "code": "R10.31",
                    "description": "Right lower quadrant pain",
                    "confidence": 0.90,
                    "rationale": "Localized abdominal pain symptom",
                    "flags": [],
                    "web_sources": []
                }
            ],
            "hcpcs_codes": [
                {
                    "code": "J0696",
                    "description": "Injection, ceftriaxone sodium, per 250 mg",
                    "confidence": 0.60,
                    "rationale": "Prophylactic antibiotic administration",
                    "flags": ["CONFIRMATION_NEEDED"],
                    "web_sources": ["HCPCS Level II"]
                }
            ],
            "medical_necessity": {
                "validated": True,
                "comments": "Emergency evaluation and potential surgery medically necessary"
            },
            "overall_confidence": 0.78,
            "flags": ["CONFIRMATION_NEEDED"],
            "recommendations": [
                "Confirm operative report details",
                "Document antibiotic administration",
                "Include imaging results if available"
            ],
            "search_queries": [
                "acute appendicitis ICD-10 2025",
                "laparoscopic appendectomy CPT",
                "ED visit coding guidelines"
            ]
        }

    def _diabetes_analysis(self) -> Dict[str, Any]:
        return {
            "report_summary": "Routine diabetes management and follow-up care.",
            "cpt_codes": [
                {
                    "code": "99213",
                    "description": "Office/outpatient visit, established patient",
                    "modifiers": [],
                    "confidence": 0.80,
                    "rationale": "Established patient office visit",
                    "flags": [],
                    "web_sources": ["CPT E/M Guidelines"]
                },
                {
                    "code": "83036",
                    "description": "Hemoglobin A1c test",
                    "modifiers": [],
                    "confidence": 0.85,
                    "rationale": "Diabetes monitoring lab test",
                    "flags": [],
                    "web_sources": ["CPT Laboratory Codes"]
                }
            ],
            "icd10_codes": [
                {
                    "code": "E11.9",
                    "description": "Type 2 diabetes mellitus without complications",
                    "confidence": 0.75,
                    "rationale": "Primary diabetes diagnosis",
                    "flags": [],
                    "web_sources": ["ICD-10-CM"]
                },
                {
                    "code": "Z79.4",
                    "description": "Long-term use of insulin",
                    "confidence": 0.60,
                    "rationale": "Diabetes medication management",
                    "flags": ["CONFIRMATION_NEEDED"],
                    "web_sources": []
                }
            ],
            "hcpcs_codes": [
                {
                    "code": "A4230",
                    "description": "Insulin syringe with needle, 1cc or less",
                    "confidence": 0.50,
                    "rationale": "Diabetes supplies",
                    "flags": ["CONFIRMATION_NEEDED"],
                    "web_sources": ["HCPCS Diabetes Supplies"]
                }
            ],
            "medical_necessity": {
                "validated": True,
                "comments": "Routine diabetes care medically necessary"
            },
            "overall_confidence": 0.72,
            "flags": [],
            "recommendations": [
                "Document specific diabetes type",
                "Include latest lab values",
                "Specify current medications"
            ],
            "search_queries": [
                "type 2 diabetes ICD-10",
                "A1c testing CPT",
                "diabetes monitoring codes"
            ]
        }

    def _hypertension_analysis(self) -> Dict[str, Any]:
        return {
            "report_summary": "Hypertension management and medication adjustment.",
            "cpt_codes": [
                {
                    "code": "99214",
                    "description": "Office/outpatient visit, established patient",
                    "modifiers": [],
                    "confidence": 0.78,
                    "rationale": "Moderate complexity office visit",
                    "flags": [],
                    "web_sources": ["CPT E/M Guidelines"]
                }
            ],
            "icd10_codes": [
                {
                    "code": "I10",
                    "description": "Essential (primary) hypertension",
                    "confidence": 0.85,
                    "rationale": "Primary hypertension diagnosis",
                    "flags": [],
                    "web_sources": ["ICD-10-CM"]
                }
            ],
            "hcpcs_codes": [],
            "medical_necessity": {
                "validated": True,
                "comments": "Hypertension management medically necessary"
            },
            "overall_confidence": 0.75,
            "flags": [],
            "recommendations": [
                "Document blood pressure readings",
                "Specify current antihypertensive medications",
                "Include cardiovascular risk factors"
            ],
            "search_queries": [
                "essential hypertension ICD-10",
                "office visit CPT established patient"
            ]
        }

    def _general_analysis(self, patient_description: str) -> Dict[str, Any]:
        return {
            "report_summary": f"General medical case analysis: {patient_description[:100]}...",
            "cpt_codes": [
                {
                    "code": "99213",
                    "description": "Office/outpatient visit, established patient",
                    "modifiers": [],
                    "confidence": 0.65,
                    "rationale": "Routine evaluation and management",
                    "flags": [],
                    "web_sources": ["CPT E/M Guidelines"]
                }
            ],
            "icd10_codes": [
                {
                    "code": "Z00.00",
                    "description": "Encounter for general adult medical examination",
                    "confidence": 0.60,
                    "rationale": "General medical examination",
                    "flags": [],
                    "web_sources": ["ICD-10-CM"]
                }
            ],
            "hcpcs_codes": [],
            "medical_necessity": {
                "validated": True,
                "comments": "General medical care appears appropriate"
            },
            "overall_confidence": 0.60,
            "flags": ["GENERAL_ANALYSIS"],
            "recommendations": [
                "Provide more specific clinical details",
                "Include symptom duration and severity",
                "Specify diagnostic test results"
            ],
            "search_queries": [
                "office visit CPT coding",
                "general exam ICD-10"
            ]
        }

medical_agent = MedicalCodingAgent()

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Medical Coding API is running", 
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/analyze", response_model=CodingResponse)
async def analyze_medical_case(request: CodingRequest):
    try:
        logger.info(f"Analysis request received: {len(request.patient_description)} chars")
        
        # Input validation
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
        "description": "AI-powered medical coding analysis API",
        "endpoints": {
            "POST /analyze": "Analyze patient descriptions for medical coding",
            "GET /health": "Health check",
            "GET /info": "API information"
        },
        "deployment": "Render"
    }

# Error handlers
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

# Production setup - Render will use this
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
