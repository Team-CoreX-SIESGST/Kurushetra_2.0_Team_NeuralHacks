"""
Uploads API endpoint for OmniSearch AI.
Handles file uploads, saves files locally, and enqueues processing jobs.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import os
import shutil
import tempfile
from datetime import datetime
from app.services.storage import StorageService
from app.services.ingest import IngestService
from app.middlewares.auth import verify_token
import json
import asyncio

router = APIRouter(prefix="/api/v1", tags=["uploads"])

# Local storage for uploaded files before processing
UPLOAD_DIR = "data/uploads"
PROCESSING_STATUS_DIR = "data/processing_status"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSING_STATUS_DIR, exist_ok=True)

# In-memory status tracking (in production, use Redis or database)
processing_status = {}

async def process_file_background(file_path: str, filename: str, workspace_id: str, file_id: str, user_id: str):
    """
    Background task to process uploaded file with robust error handling.
    """
    status_file = os.path.join(PROCESSING_STATUS_DIR, f"{file_id}.json")
    
    try:
        # Update status to processing
        status_data = {
            "file_id": file_id,
            "filename": filename,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": "processing",
            "started_at": datetime.now().isoformat(),
            "progress": 0,
            "current_step": "Initializing processing"
        }
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
        
        processing_status[file_id] = status_data
        print(f"Starting processing for file: {filename} (ID: {file_id})")
        
        # Step 1: Store file in storage system
        try:
            storage_service = StorageService()
            
            with open(file_path, 'rb') as file_obj:
                status_data["progress"] = 10
                status_data["current_step"] = "Storing file"
                processing_status[file_id] = status_data
                with open(status_file, 'w') as f:
                    json.dump(status_data, f)
                
                storage_result = await storage_service.store_file(
                    file_obj,
                    filename,
                    workspace_id,
                    file_id
                )
                
                if storage_result.get('status') == 'error':
                    raise Exception(f"Storage failed: {storage_result.get('error', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"File storage step failed: {str(e)}")
        
        # Step 2: Process file for indexing (optional)
        try:
            status_data["progress"] = 50
            status_data["current_step"] = "Processing file content (optional)"
            processing_status[file_id] = status_data
            with open(status_file, 'w') as f:
                json.dump(status_data, f)
            
            # Try to initialize ingest service
            ingest_service = IngestService()
            
            with open(file_path, 'rb') as file_obj:
                processing_result = await ingest_service.process_file(
                    file_obj,
                    filename,
                    workspace_id,
                    file_id
                )
                
                if processing_result.get('status') == 'error':
                    print(f"AI processing failed but file is stored: {processing_result.get('error')}")
                    # Continue - file is stored even if AI processing fails
                    processing_result = {
                        'chunks_created': 0,
                        'total_characters': 0,
                        'vector_count': 0
                    }
        except Exception as e:
            print(f"AI processing failed but file is stored: {str(e)}")
            # Continue - file is stored even if AI processing fails
            processing_result = {
                'chunks_created': 0,
                'total_characters': 0,
                'vector_count': 0
            }
        
        # Update status to completed
        status_data.update({
            "status": "completed",
            "progress": 100,
            "current_step": "Completed",
            "completed_at": datetime.now().isoformat(),
            "chunks_created": processing_result.get('chunks_created', 0),
            "total_characters": processing_result.get('total_characters', 0),
            "vector_count": processing_result.get('vector_count', 0)
        })
        
        processing_status[file_id] = status_data
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
        
        print(f"Successfully processed file: {filename} (ID: {file_id})")
        
    except Exception as e:
        error_msg = str(e)
        print(f"Background processing failed for {filename}: {error_msg}")
        
        # Update status to error
        status_data = {
            "file_id": file_id,
            "filename": filename,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": "error",
            "progress": 0,
            "current_step": "Error",
            "error": error_msg,
            "failed_at": datetime.now().isoformat()
        }
        
        processing_status[file_id] = status_data
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            print(f"Failed to clean up temporary file {file_path}: {e}")

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    file_id: Optional[str] = Form(None),
    current_user: dict = Depends(verify_token)
):
    """
    Upload a file, save it locally, and queue for background processing.
    
    Args:
        background_tasks: FastAPI background tasks
        workspace_id: Workspace identifier
        file: File to upload
        file_id: Optional custom file ID
        current_user: Authenticated user
    
    Returns:
        JSON response with file_id, filename, and status
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file size (10MB limit)
        if hasattr(file, 'size') and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        supported_extensions = ['.pdf', '.docx', '.txt']
        if file_extension not in supported_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type {file_extension}. Supported types: {', '.join(supported_extensions)}"
            )
        
        # Generate file ID if not provided
        if not file_id:
            file_id = str(uuid.uuid4())
        
        user_id = current_user.get('user_id', 'unknown')
        
        # Create workspace directory
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Save file locally first
        file_path = os.path.join(workspace_dir, f"{file_id}_{file.filename}")
        
        print(f"Saving file to: {file_path}")
        
        # Save uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        print(f"File saved successfully: {file.filename} ({file_size} bytes)")
        
        # Initialize status
        status_data = {
            "file_id": file_id,
            "filename": file.filename,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": "uploaded",
            "progress": 0,
            "current_step": "File uploaded, queued for processing",
            "uploaded_at": datetime.now().isoformat(),
            "file_size": file_size
        }
        
        processing_status[file_id] = status_data
        
        # Save status to file
        status_file = os.path.join(PROCESSING_STATUS_DIR, f"{file_id}.json")
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
        
        # Queue background processing
        background_tasks.add_task(
            process_file_background, 
            file_path, 
            file.filename, 
            workspace_id, 
            file_id, 
            user_id
        )
        
        # Return immediate response
        return JSONResponse(
            status_code=202,  # Accepted
            content={
                "file_id": file_id,
                "filename": file.filename,
                "workspace_id": workspace_id,
                "status": "uploaded",
                "message": "File uploaded successfully and queued for processing",
                "file_size": file_size,
                "processing_status_url": f"/api/v1/status/{file_id}?workspace_id={workspace_id}",
                "uploaded_at": datetime.now().isoformat()
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
        # Check in-memory status first
        if file_id in processing_status:
            status_data = processing_status[file_id]
            return JSONResponse(
                status_code=200,
                content={
                    **status_data,
                    "last_checked": datetime.now().isoformat()
                }
            )
        
        # Check status file
        status_file = os.path.join(PROCESSING_STATUS_DIR, f"{file_id}.json")
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status_data = json.load(f)
                
            # Update in-memory cache
            processing_status[file_id] = status_data
            
            return JSONResponse(
                status_code=200,
                content={
                    **status_data,
                    "last_checked": datetime.now().isoformat()
                }
            )
        
        # File not found in processing system
        raise HTTPException(status_code=404, detail="File processing status not found")
        
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

@router.get("/files")
async def list_files(
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    List all files in a workspace.
    
    Args:
        workspace_id: Workspace identifier (from query params)
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

@router.get("/files/{workspace_id}")
async def list_workspace_files(
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    List all files in a workspace with their processing status.
    
    Args:
        workspace_id: Workspace identifier
        current_user: Authenticated user
    
    Returns:
        JSON response with list of files and their processing status
    """
    try:
        # Initialize services
        storage_service = StorageService()
        
        # List files
        files = await storage_service.list_workspace_files(workspace_id)
        
        # Add processing status to each file
        files_with_status = []
        for file_info in files:
            file_id = file_info.get('file_id')
            
            # Get processing status if available
            status_info = None
            if file_id:
                # Check in-memory status
                if file_id in processing_status:
                    status_info = processing_status[file_id]
                else:
                    # Check status file
                    status_file = os.path.join(PROCESSING_STATUS_DIR, f"{file_id}.json")
                    if os.path.exists(status_file):
                        try:
                            with open(status_file, 'r') as f:
                                status_info = json.load(f)
                                processing_status[file_id] = status_info  # Cache it
                        except Exception as e:
                            print(f"Failed to read status file for {file_id}: {e}")
            
            file_with_status = {
                **file_info,
                "processing_status": status_info.get('status', 'unknown') if status_info else 'unknown',
                "progress": status_info.get('progress', 0) if status_info else 0,
                "current_step": status_info.get('current_step', 'N/A') if status_info else 'N/A'
            }
            
            if status_info and 'error' in status_info:
                file_with_status['error'] = status_info['error']
            
            files_with_status.append(file_with_status)
        
        return JSONResponse(
            status_code=200,
            content={
                "workspace_id": workspace_id,
                "files": files_with_status,
                "total_files": len(files_with_status),
                "retrieved_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        print(f"File listing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File listing failed: {str(e)}"
        )

@router.post("/upload/test")
async def test_upload_simple(
    workspace_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Simple test upload endpoint without authentication for debugging.
    """
    try:
        # Validate file
        if not file.filename:
            return JSONResponse(
                status_code=400,
                content={"error": "No filename provided"}
            )
        
        # Generate file ID
        file_id = str(uuid.uuid4())
        
        # Create workspace directory  
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Save file locally
        file_path = os.path.join(workspace_dir, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "filename": file.filename,
                "workspace_id": workspace_id,
                "file_size": file_size,
                "file_path": file_path,
                "message": "Test upload successful"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Test upload failed: {str(e)}"}
        )

@router.get("/processing/status")
async def get_all_processing_status(
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(verify_token)
):
    """
    Get all processing statuses, optionally filtered by workspace.
    
    Args:
        workspace_id: Optional workspace filter
        current_user: Authenticated user
    
    Returns:
        JSON response with all processing statuses
    """
    try:
        all_statuses = []
        
        # Get all status files
        for status_filename in os.listdir(PROCESSING_STATUS_DIR):
            if not status_filename.endswith('.json'):
                continue
                
            file_id = status_filename.replace('.json', '')
            
            try:
                status_file = os.path.join(PROCESSING_STATUS_DIR, status_filename)
                with open(status_file, 'r') as f:
                    status_data = json.load(f)
                
                # Filter by workspace if specified
                if workspace_id and status_data.get('workspace_id') != workspace_id:
                    continue
                    
                all_statuses.append(status_data)
                
                # Update in-memory cache
                processing_status[file_id] = status_data
                
            except Exception as e:
                print(f"Failed to read status file {status_filename}: {e}")
                continue
        
        # Sort by upload time (most recent first)
        all_statuses.sort(
            key=lambda x: x.get('uploaded_at', x.get('started_at', '')), 
            reverse=True
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "statuses": all_statuses,
                "total_files": len(all_statuses),
                "workspace_filter": workspace_id,
                "retrieved_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        print(f"Status retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Status retrieval failed: {str(e)}"
        )
