"""
Files API endpoint for OmniSearch AI.
Handles file retrieval and page access for provenance.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
from app.services.storage import StorageService
from app.services.vectordb import VectorDBService
from app.middlewares.auth import verify_token

router = APIRouter(prefix="/api/v1", tags=["files"])

@router.get("/file/{file_id}")
async def get_file_info(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get file information and metadata.
    
    Args:
        file_id: File identifier
        workspace_id: Workspace identifier
        current_user: Authenticated user
    
    Returns:
        JSON response with file information
    """
    try:
        # Initialize services
        storage_service = StorageService()
        
        # Try to get file info (assuming PDF for now)
        file_info = await storage_service.retrieve_file(
            file_id,
            workspace_id,
            f"{file_id}.pdf"
        )
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "workspace_id": workspace_id,
                "file_info": file_info,
                "retrieved_at": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"File info retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File info retrieval failed: {str(e)}"
        )

@router.get("/file/{file_id}/page/{page_number}")
async def get_file_page(
    file_id: str,
    page_number: int,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get specific page content from a file.
    
    Args:
        file_id: File identifier
        page_number: Page number (1-based)
        workspace_id: Workspace identifier
        current_user: Authenticated user
    
    Returns:
        JSON response with page content
    """
    try:
        if page_number < 1:
            raise HTTPException(status_code=400, detail="Page number must be 1 or greater")
        
        # Initialize services
        vector_db = VectorDBService(workspace_id)
        await vector_db.initialize()
        
        # Search for chunks from the specific page
        # This is a simplified approach - in production, you might want to store page metadata
        search_results = vector_db.search(
            query_vector=None,  # We'll filter by metadata instead
            top_k=100  # Get more results to find the page
        )
        
        # Filter results by page number
        page_chunks = []
        for result in search_results:
            if result.get('file_id') == file_id and result.get('page') == page_number:
                page_chunks.append({
                    "chunk_id": result.get('id', result.get('vector_id', '')),
                    "text": result.get('text', ''),
                    "chunk_index": result.get('chunk_index', 0),
                    "start_char": result.get('start_char', 0),
                    "end_char": result.get('end_char', 0)
                })
        
        if not page_chunks:
            raise HTTPException(
                status_code=404,
                detail=f"Page {page_number} not found in file {file_id}"
            )
        
        # Sort chunks by chunk_index to maintain order
        page_chunks.sort(key=lambda x: x.get('chunk_index', 0))
        
        # Combine text from all chunks on the page
        page_text = ""
        for chunk in page_chunks:
            page_text += chunk['text'] + "\n"
        
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "workspace_id": workspace_id,
                "page_number": page_number,
                "page_content": page_text.strip(),
                "chunks": page_chunks,
                "total_chunks": len(page_chunks),
                "retrieved_at": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Page retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Page retrieval failed: {str(e)}"
        )

@router.get("/file/{file_id}/chunks")
async def get_file_chunks(
    file_id: str,
    workspace_id: str,
    page: Optional[int] = Query(None, description="Filter by page number"),
    limit: int = Query(50, description="Maximum number of chunks to return"),
    current_user: dict = Depends(verify_token)
):
    """
    Get chunks from a file, optionally filtered by page.
    
    Args:
        file_id: File identifier
        workspace_id: Workspace identifier
        page: Optional page number filter
        limit: Maximum number of chunks to return
        current_user: Authenticated user
    
    Returns:
        JSON response with file chunks
    """
    try:
        # Initialize services
        vector_db = VectorDBService(workspace_id)
        await vector_db.initialize()
        
        # Get all chunks for the file
        search_results = vector_db.search(
            query_vector=None,  # We'll filter by metadata instead
            top_k=1000  # Get more results to find all chunks
        )
        
        # Filter results by file_id and optionally by page
        file_chunks = []
        for result in search_results:
            if result.get('file_id') == file_id:
                if page is None or result.get('page') == page:
                    chunk = {
                        "chunk_id": result.get('id', result.get('vector_id', '')),
                        "text": result.get('text', ''),
                        "page": result.get('page', 1),
                        "chunk_index": result.get('chunk_index', 0),
                        "start_char": result.get('start_char', 0),
                        "end_char": result.get('end_char', 0),
                        "score": result.get('score', 0),
                        "timestamp": result.get('timestamp', '')
                    }
                    file_chunks.append(chunk)
        
        # Sort chunks by page and chunk_index
        file_chunks.sort(key=lambda x: (x.get('page', 1), x.get('chunk_index', 0)))
        
        # Apply limit
        if limit > 0:
            file_chunks = file_chunks[:limit]
        
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "workspace_id": workspace_id,
                "chunks": file_chunks,
                "total_chunks": len(file_chunks),
                "page_filter": page,
                "limit_applied": limit,
                "retrieved_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        print(f"Chunk retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chunk retrieval failed: {str(e)}"
        )

@router.get("/file/{file_id}/download")
async def download_file(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Download a file.
    
    Args:
        file_id: File identifier
        workspace_id: Workspace identifier
        current_user: Authenticated user
    
    Returns:
        File response for download
    """
    try:
        # Initialize services
        storage_service = StorageService()
        
        # Get file info
        file_info = await storage_service.retrieve_file(
            file_id,
            workspace_id,
            f"{file_id}.pdf"  # Assuming PDF for now
        )
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # For local storage, return the file directly
        if file_info.get('storage_type') == 'local':
            file_path = file_info.get('storage_path')
            if os.path.exists(file_path):
                return FileResponse(
                    path=file_path,
                    filename=file_info.get('filename', f"{file_id}.pdf"),
                    media_type='application/pdf'
                )
            else:
                raise HTTPException(status_code=404, detail="File not found on disk")
        
        # For S3 storage, redirect to presigned URL
        elif file_info.get('storage_type') == 's3':
            presigned_url = file_info.get('presigned_url')
            if presigned_url:
                return JSONResponse(
                    status_code=200,
                    content={
                        "download_url": presigned_url,
                        "expires_in": "1 hour",
                        "message": "Use the download_url to access the file"
                    }
                )
            else:
                raise HTTPException(status_code=500, detail="Download URL not available")
        
        else:
            raise HTTPException(status_code=500, detail="Unsupported storage type")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"File download failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File download failed: {str(e)}"
        )

@router.get("/file/{file_id}/metadata")
async def get_file_metadata(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get comprehensive metadata for a file.
    
    Args:
        file_id: File identifier
        workspace_id: Workspace identifier
        current_user: Authenticated user
    
    Returns:
        JSON response with file metadata
    """
    try:
        # Initialize services
        storage_service = StorageService()
        vector_db = VectorDBService(workspace_id)
        
        # Get storage metadata
        storage_info = await storage_service.retrieve_file(
            file_id,
            workspace_id,
            f"{file_id}.pdf"
        )
        
        if not storage_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get vector database metadata
        await vector_db.initialize()
        search_results = vector_db.search(
            query_vector=None,
            top_k=1000
        )
        
        # Filter chunks for this file
        file_chunks = [r for r in search_results if r.get('file_id') == file_id]
        
        # Calculate metadata
        total_chunks = len(file_chunks)
        total_pages = len(set(chunk.get('page', 1) for chunk in file_chunks))
        total_characters = sum(len(chunk.get('text', '')) for chunk in file_chunks)
        
        # Get page statistics
        page_stats = {}
        for chunk in file_chunks:
            page = chunk.get('page', 1)
            if page not in page_stats:
                page_stats[page] = {
                    "chunk_count": 0,
                    "character_count": 0
                }
            page_stats[page]["chunk_count"] += 1
            page_stats[page]["character_count"] += len(chunk.get('text', ''))
        
        metadata = {
            "file_id": file_id,
            "workspace_id": workspace_id,
            "storage_info": storage_info,
            "vector_stats": {
                "total_chunks": total_chunks,
                "total_pages": total_pages,
                "total_characters": total_characters,
                "average_chunk_size": total_characters / total_chunks if total_chunks > 0 else 0
            },
            "page_statistics": page_stats,
            "chunk_distribution": {
                "chunks_per_page": {page: stats["chunk_count"] for page, stats in page_stats.items()}
            },
            "retrieved_at": datetime.now().isoformat()
        }
        
        return JSONResponse(
            status_code=200,
            content=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Metadata retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Metadata retrieval failed: {str(e)}"
        )
