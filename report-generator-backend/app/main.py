
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.knowledge_routes import router as knowledge_router
from app.routers.report_routes import router as report_router
from app.services.ollama_service import MODEL_NAME


app = FastAPI(
    title="AI-Assisted Accomplishment Report Generator",
    description="AI-assisted faculty accomplishment report generation system.",
    version="1.0.0"
)


# Allow communication with the React frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers.
app.include_router(knowledge_router)
app.include_router(report_router)


@app.get("/")
def home():
    return {
        "message": "Accomplishment Report Generator is running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "model": MODEL_NAME
    }
