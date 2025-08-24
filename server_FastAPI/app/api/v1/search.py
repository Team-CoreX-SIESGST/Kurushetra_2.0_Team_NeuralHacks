"""
Search API endpoint for OmniSearch AI.
Simplified Gemini-only search implementation.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from app.services.gemini_rag_service import GeminiRAGService
from app.services.web_search import WebSearchService
from app.middlewares.auth import verify_token

router = APIRouter(prefix="/api/v1", tags=["search"])

class SearchRequest(BaseModel):
    workspace_id: str
    query: str
    top_k: int = 10
    include_web: bool = True
    summarize: bool = True

class SearchResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]
    processing_time: float
    metadata: Dict[str, Any]

@router.post("/search")
async def search_documents(
    request: SearchRequest = Body(...),
    current_user: dict = Depends(verify_token)
):
    """
    Search documents using Gemini RAG pipeline.
    
    Args:
        request: Search request with query and parameters
        current_user: Authenticated user
    
    Returns:
        JSON response with answer, confidence, and sources
    """
    start_time = datetime.now()
    
    try:
        # Initialize Gemini RAG service
        gemini_rag_service = GeminiRAGService()
        web_search_service = WebSearchService()
        
        # Step 1: Generate search tags for the query
        search_tags = await gemini_rag_service.generate_search_tags_from_query(request.query)
        
        # Step 2: Perform web search if enabled
        web_results = []
        if request.include_web:
            web_results = await web_search_service.search_web_with_tags(search_tags, max_results=request.top_k)
        
        # Step 3: Generate comprehensive answer using Gemini
        answer_result = await gemini_rag_service.generate_answer_from_query_and_web(
            query=request.query,
            web_results=web_results,
            workspace_id=request.workspace_id
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=200,
            content={
                "answer": answer_result.get('answer', 'No answer generated'),
                "confidence": answer_result.get('confidence', 0.0),
                "sources": web_results,
                "processing_time": processing_time,
                "metadata": {
                    "intent": "gemini_rag_search",
                    "model_used": "gemini-2.0-flash-exp",
                    "search_type": "gemini_rag_pipeline",
                    "web_results": len(web_results),
                    "summarized": request.summarize
                }
            }
        )
        
    except Exception as e:
        print(f"Search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search processing failed: {str(e)}"
        )

@router.get("/search/simple")
async def simple_search(
    workspace_id: str,
    query: str,
    top_k: int = 5,
    current_user: dict = Depends(verify_token)
):
    """
    Simple search using Gemini without web enhancement.
    """
    try:
        gemini_rag_service = GeminiRAGService()
        
        # Generate simple answer using Gemini
        answer_result = await gemini_rag_service.generate_simple_answer(
            query=query,
            workspace_id=workspace_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "query": query,
                "workspace_id": workspace_id,
                "answer": answer_result.get('answer', 'No answer generated'),
                "confidence": answer_result.get('confidence', 0.0),
                "processing_time": answer_result.get('processing_time', 0.0)
            }
        )
        
    except Exception as e:
        print(f"Simple search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Simple search failed: {str(e)}"
        )

@router.get("/search/stats/{workspace_id}")
async def get_search_stats(
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get search statistics for a workspace.
    """
    try:
        # For Gemini-only implementation, return basic stats
        return JSONResponse(
            status_code=200,
            content={
                "workspace_id": workspace_id,
                "stats": {
                    "workspace_id": workspace_id,
                    "search_engine": "gemini_rag",
                    "model": "gemini-2.0-flash-exp",
                    "last_updated": datetime.now().isoformat()
                },
                "retrieved_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        print(f"Failed to get search stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get search stats: {str(e)}"
        )
