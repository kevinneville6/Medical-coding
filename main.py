from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI()

class AnalysisRequest(BaseModel):
    patient_description: str

class AnalysisResponse(BaseModel):
    status: str
    message: str
    report_id: str

@app.get("/")
def root():
    return {"status": "healthy", "message": "Medical Coding API"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "medical-coding-api"}

@app.post("/analyze")
def analyze(request: AnalysisRequest):
    return {
        "status": "success", 
        "message": "Analysis completed",
        "report_id": "test-123"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
