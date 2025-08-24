"""
Uploads API endpoint for OmniSearch AI.
Handles file uploads and enqueues indexing jobs.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
from datetime import datetime
from app.services.storage import StorageService
from app.services.ingest import IngestService
from app.middlewares.auth import verify_token
from app.utils.api_response import APIResponse

router = APIRouter(prefix="/api/v1", tags=["uploads"])

@router.post("/upload")
async def upload_file(
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    file_id: Optional[str] = Form(None),
    current_user: dict = Depends(verify_token)
):
    """
    Upload a file and enqueue indexing job.
    
    Args:
        workspace_id: Workspace identifier
        file: File to upload
        file_id: Optional custom file ID
        current_user: Authenticated user
    
    Returns:
        JSON response with file_id, filename, status, and message
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Generate file ID if not provided
        if not file_id:
            file_id = str(uuid.uuid4())
        
        # Initialize services
        storage_service = StorageService()
        ingest_service = IngestService()
        
        # Store file
        storage_result = await storage_service.store_file(
            file.file,
            file.filename,
            workspace_id,
            file_id
        )
        
        if storage_result.get('status') == 'error':
            raise HTTPException(
                status_code=500,
                detail=f"Storage failed: {storage_result.get('error', 'Unknown error')}"
            )
        
        # Process file for indexing
        processing_result = await ingest_service.process_file(
            file.file,
            file.filename,
            workspace_id,
            file_id
        )
        
        if processing_result.get('status') == 'error':
            # File was stored but processing failed
            # In production, you might want to delete the stored file
            return JSONResponse(
                status_code=202,
                content={
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "uploaded",
                    "message": f"File uploaded but indexing failed: {processing_result.get('error')}",
                    "warning": "File is stored but not searchable"
                }
            )
        
        # Success response
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "filename": file.filename,
                "status": "uploaded",
                "message": "Indexing queued",
                "details": {
                    "chunks_created": processing_result.get('chunks_created', 0),
                    "total_characters": processing_result.get('total_characters', 0),
                    "vector_count": processing_result.get('vector_count', 0)
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/status/{file_id}")
async def get_file_status(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get the processing status of a file.
    
    Args:
        file_id: File identifier
        workspace_id: Workspace identifier
        current_user: Authenticated user
    
    Returns:
        JSON response with file status and details
    """
    try:
        # Initialize services
        storage_service = StorageService()
        
        # Get file information
        file_info = await storage_service.retrieve_file(
            file_id,
            workspace_id,
            f"{file_id}.pdf"  # Assuming PDF for now
        )
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # In a production system, you might want to check a job queue
        # or database for actual processing status
        status = "processed" if file_info else "uploaded"
        
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "workspace_id": workspace_id,
                "status": status,
                "file_info": file_info,
                "last_checked": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Status check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )

@router.delete("/file/{file_id}")
async def delete_file(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Delete a file and its associated data.
    
    Args:
        file_id: File identifier
        workspace_id: Workspace identifier
        current_user: Authenticated user
    
    Returns:
        JSON response confirming deletion
    """
    try:
        # Initialize services
        storage_service = StorageService()
        
        # Get file info first
        file_info = await storage_service.retrieve_file(
            file_id,
            workspace_id,
            f"{file_id}.pdf"  # Assuming PDF for now
        )
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete file
        success = await storage_service.delete_file(
            file_id,
            workspace_id,
            f"{file_id}.pdf"
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete file")
        
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "workspace_id": workspace_id,
                "status": "deleted",
                "message": "File deleted successfully",
                "deleted_at": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"File deletion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File deletion failed: {str(e)}"
        )

@router.get("/files/{workspace_id}")
async def list_workspace_files(
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    List all files in a workspace.
    
    Args:
        workspace_id: Workspace identifier
        current_user: Authenticated user
    
    Returns:
        JSON response with list of files
    """
    try:
        # Initialize services
        storage_service = StorageService()
        
        # List files
        files = await storage_service.list_workspace_files(workspace_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "workspace_id": workspace_id,
                "files": files,
                "total_files": len(files),
                "retrieved_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        print(f"File listing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File listing failed: {str(e)}"
        )
