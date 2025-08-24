from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import connect_db
from app.routes import user_routes
from app.api.v1 import uploads, search, files
from app.config import settings

app = FastAPI(
    title="OmniSearch AI API",
    description="AI-powered orchestrator that ingests user files, enriches with web results, routes tasks to the right model via Ollama, and returns provenance-backed answers.",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(user_routes.router, prefix="/api")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    await connect_db()

@app.get("/")
async def root():
    return {
        "message": "OmniSearch AI API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.server_port,
        reload=True
    )