from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "healthy", "message": "Medical Coding API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze(patient_description: str):
    return {
        "status": "success",
        "report_id": "docker-123",
        "analysis": {
            "summary": "Analysis completed",
            "cpt_codes": [{"code": "99213", "description": "Office visit"}]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
