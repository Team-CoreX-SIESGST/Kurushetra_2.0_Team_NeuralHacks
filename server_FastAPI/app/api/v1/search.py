"""
Search API endpoint for OmniSearch AI.
Orchestrates embeddings, vector DB search, web fetch, reranker, and final summarizer.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from app.services.model_router import ModelRouter
from app.services.embeddings import EmbeddingsService
from app.services.vectordb import VectorDBService
from app.services.reranker import RerankerService
from app.services.summarizer import SummarizerService
from app.services.web_search import WebSearchService
from app.middlewares.auth import verify_token

router = APIRouter(prefix="/api/v1", tags=["search"])

class SearchRequest(BaseModel):
    workspace_id: str
    query: str
    top_k: int = 10
    include_web: bool = True
    rerank: bool = True
    summarize: bool = True

class SearchResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]
    raw_chunks: List[Dict[str, Any]]
    processing_time: float
    metadata: Dict[str, Any]

@router.post("/search")
async def search_documents(
    request: SearchRequest = Body(...),
    current_user: dict = Depends(verify_token)
):
    """
    Search documents using the full AI pipeline.
    
    Args:
        request: Search request with query and parameters
        current_user: Authenticated user
    
    Returns:
        JSON response with answer, confidence, sources, and raw chunks
    """
    start_time = datetime.now()
    
    try:
        # Initialize services
        model_router = ModelRouter()
        embeddings_service = EmbeddingsService()
        vector_db = VectorDBService(request.workspace_id)
        reranker_service = RerankerService()
        summarizer_service = SummarizerService()
        web_search_service = WebSearchService()
        
        # Step 1: Model routing (intent classification)
        routing_result = await model_router.route_query(request.query)
        intent = routing_result.get('intent', 'research_longform')
        model_config = routing_result.get('model_config', {})
        
        # Step 2: Generate query embeddings
        await embeddings_service.initialize()
        query_embedding = embeddings_service.generate_single_embedding(request.query)
        
        # Step 3: Vector database search
        await vector_db.initialize(embeddings_service.get_embedding_dimension())
        search_results = vector_db.search(query_embedding, request.top_k)
        
        if not search_results:
            # No results found in vector database
            if request.include_web:
                # Try web search only
                web_results = await web_search_service.search_web(request.query, max_results=3)
                if web_results:
                    # Generate summary from web results only
                    summary = await summarizer_service.generate_summary(
                        request.query,
                        web_results,
                        model_config.get('model_path')
                    )
                    
                    return JSONResponse(
                        status_code=200,
                        content={
                            "answer": summary.get('answer', 'INSUFFICIENT_EVIDENCE'),
                            "confidence": summary.get('confidence', 0.0),
                            "sources": summary.get('sources', []),
                            "raw_chunks": [],
                            "processing_time": (datetime.now() - start_time).total_seconds(),
                            "metadata": {
                                "intent": intent,
                                "model_used": model_config.get('name', 'unknown'),
                                "search_type": "web_only",
                                "vector_results": 0,
                                "web_results": len(web_results)
                            }
                        }
                    )
            
            # No results at all
            return JSONResponse(
                status_code=200,
                content={
                    "answer": "INSUFFICIENT_EVIDENCE",
                    "confidence": 0.0,
                    "sources": [],
                    "raw_chunks": [],
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "metadata": {
                        "intent": intent,
                        "model_used": model_config.get('name', 'unknown'),
                        "search_type": "no_results",
                        "vector_results": 0,
                        "web_results": 0
                    }
                }
            )
        
        # Step 4: Web enrichment (if requested)
        enriched_results = search_results
        if request.include_web:
            enriched_results = await web_search_service.enrich_search_results(
                request.query,
                search_results,
                include_web=True
            )
        
        # Step 5: Reranking (if requested)
        final_results = enriched_results
        if request.rerank and len(enriched_results) > 1:
            final_results = await reranker_service.rerank_results(
                request.query,
                enriched_results,
                request.top_k
            )
        
        # Step 6: Final summarization (if requested)
        if request.summarize:
            try:
                summary = await summarizer_service.generate_summary(
                    request.query,
                    final_results,
                    model_config.get('model_path')
                )
                
                # Check if summary generation was successful
                if not summary or not summary.get('answer'):
                    print("Summary generation returned empty result, using fallback")
                    summary = {
                        "answer": f"Found {len(final_results)} relevant results for your query.",
                        "confidence": 0.5,
                        "sources": [],
                        "code": None
                    }
            except Exception as summarize_error:
                print(f"Summarization failed with error: {summarize_error}")
                # Create fallback summary
                summary = {
                    "answer": f"Found {len(final_results)} relevant results for your query, but summarization failed.",
                    "confidence": 0.3,
                    "sources": [],
                    "code": None
                }
            
            # Prepare sources for response
            sources = []
            for i, result in enumerate(final_results[:5]):  # Top 5 sources
                source = {
                    "file_id": result.get('file_id', ''),
                    "filename": result.get('filename', ''),
                    "page": result.get('page', ''),
                    "snippet": result.get('text', '')[:200] + "..." if len(result.get('text', '')) > 200 else result.get('text', ''),
                    "score": result.get('score', 0),
                    "url": result.get('url', '')
                }
                sources.append(source)
            
            # Prepare raw chunks for response
            raw_chunks = []
            for result in final_results:
                chunk = {
                    "id": result.get('id', result.get('vector_id', '')),
                    "text": result.get('text', ''),
                    "score": result.get('score', 0)
                }
                raw_chunks.append(chunk)
            
            return JSONResponse(
                status_code=200,
                content={
                    "answer": summary.get('answer', 'INSUFFICIENT_EVIDENCE'),
                    "confidence": summary.get('confidence', 0.0),
                    "sources": sources,
                    "raw_chunks": raw_chunks,
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "metadata": {
                        "intent": intent,
                        "model_used": model_config.get('name', 'unknown'),
                        "search_type": "full_pipeline",
                        "vector_results": len(search_results),
                        "web_results": len(enriched_results) - len(search_results),
                        "reranked": request.rerank,
                        "summarized": request.summarize
                    }
                }
            )
        else:
            # Return raw results without summarization
            sources = []
            for result in final_results[:5]:
                source = {
                    "file_id": result.get('file_id', ''),
                    "filename": result.get('filename', ''),
                    "page": result.get('page', ''),
                    "snippet": result.get('text', '')[:200] + "..." if len(result.get('text', '')) > 200 else result.get('text', ''),
                    "score": result.get('score', 0),
                    "url": result.get('url', '')
                }
                sources.append(source)
            
            raw_chunks = []
            for result in final_results:
                chunk = {
                    "id": result.get('id', result.get('vector_id', '')),
                    "text": result.get('text', ''),
                    "score": result.get('score', 0)
                }
                raw_chunks.append(chunk)
            
            return JSONResponse(
                status_code=200,
                content={
                    "answer": "Search completed without summarization",
                    "confidence": 0.8,  # Default confidence for raw results
                    "sources": sources,
                    "raw_chunks": raw_chunks,
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "metadata": {
                        "intent": intent,
                        "model_used": model_config.get('name', 'unknown'),
                        "search_type": "raw_results",
                        "vector_results": len(search_results),
                        "web_results": len(enriched_results) - len(search_results),
                        "reranked": request.rerank,
                        "summarized": False
                    }
                }
            )
            
    except Exception as e:
        print(f"Search failed: {e}")
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JSONResponse(
            status_code=500,
            content={
                "answer": "INSUFFICIENT_EVIDENCE",
                "confidence": 0.0,
                "sources": [],
                "raw_chunks": [],
                "processing_time": processing_time,
                "metadata": {
                    "error": str(e),
                    "search_type": "error"
                }
            }
        )

@router.get("/search/simple")
async def simple_search(
    workspace_id: str,
    query: str,
    top_k: int = 5,
    current_user: dict = Depends(verify_token)
):
    """
    Simple search without full AI pipeline.
    
    Args:
        workspace_id: Workspace identifier
        query: Search query
        top_k: Number of results to return
        current_user: Authenticated user
    
    Returns:
        JSON response with raw search results
    """
    try:
        # Initialize services
        embeddings_service = EmbeddingsService()
        vector_db = VectorDBService(workspace_id)
        
        # Generate query embeddings
        await embeddings_service.initialize()
        query_embedding = embeddings_service.generate_single_embedding(query)
        
        # Search vector database
        await vector_db.initialize(embeddings_service.get_embedding_dimension())
        search_results = vector_db.search(query_embedding, top_k)
        
        # Prepare response
        results = []
        for result in search_results:
            results.append({
                "id": result.get('id', result.get('vector_id', '')),
                "text": result.get('text', ''),
                "score": result.get('score', 0),
                "file_id": result.get('file_id', ''),
                "filename": result.get('filename', ''),
                "page": result.get('page', '')
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "query": query,
                "workspace_id": workspace_id,
                "results": results,
                "total_results": len(results),
                "search_time": datetime.now().isoformat()
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
    
    Args:
        workspace_id: Workspace identifier
        current_user: Authenticated user
    
    Returns:
        JSON response with search statistics
    """
    try:
        # Initialize services
        vector_db = VectorDBService(workspace_id)
        await vector_db.initialize()
        
        stats = vector_db.get_workspace_stats()
        
        return JSONResponse(
            status_code=200,
            content={
                "workspace_id": workspace_id,
                "stats": stats,
                "retrieved_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        print(f"Stats retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Stats retrieval failed: {str(e)}"
        )
