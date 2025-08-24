from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import connect_db
from app.routes import user_routes
from app.routes.enhanced_document_routes import router as enhanced_document_router
from app.api.v1 import uploads, search, files
from app.middlewares.rate_limiter import RateLimitMiddleware
from app.settings import settings

app = FastAPI(
    title="OmniSearch AI API",
    description="AI-powered orchestrator that ingests user files, enriches with web results, uses Gemini for RAG summaries, and provides enhanced document analysis with web enhancement.",
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

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routes
app.include_router(user_routes.router, prefix="/api")
app.include_router(enhanced_document_router)  # Enhanced document processing routes
app.include_router(uploads.router)
app.include_router(search.router) 
app.include_router(files.router)

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