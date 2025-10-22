from fastapi import FastAPI
import os
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Medical Coding API Debug")

# Log startup information
logger.info("=== APPLICATION STARTING ===")
logger.info(f"PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
logger.info(f"Python version: {os.sys.version}")

@app.on_event("startup")
async def startup_event():
    logger.info("=== FASTAPI APP STARTUP COMPLETE ===")
    logger.info("Registered endpoints:")
    for route in app.routes:
        if hasattr(route, 'methods'):
            logger.info(f"  {list(route.methods)} {route.path}")

@app.get("/")
async def root():
    logger.info("GET / endpoint called")
    return {
        "message": "Medical Coding API - ROOT", 
        "status": "working",
        "debug": True
    }

@app.get("/health")
async def health():
    logger.info("GET /health endpoint called")
    return {
        "status": "healthy", 
        "service": "medical-coding-api",
        "debug": True
    }

@app.post("/analyze")
async def analyze(patient_description: str):
    logger.info("POST /analyze endpoint called")
    return {
        "status": "success",
        "report_id": "debug-123",
        "message": "Analysis completed in debug mode",
        "debug": True
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting uvicorn on port {port}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
