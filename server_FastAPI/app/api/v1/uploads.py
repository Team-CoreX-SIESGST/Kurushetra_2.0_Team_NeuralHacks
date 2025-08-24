"""
Uploads API endpoint for OmniSearch AI.
Simplified Gemini-only file upload and storage implementation.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import os
import shutil
from datetime import datetime
from app.services.storage import StorageService
from app.middlewares.auth import verify_token
from app.middlewares.rate_limiter import validate_file_size_dependency

router = APIRouter(prefix="/api/v1", tags=["uploads"])

# Local storage for uploaded files
UPLOAD_DIR = "data/uploads"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    file_id: Optional[str] = Form(None),
    current_user: dict = Depends(verify_token)
):
    """
    Upload a file for Gemini processing.
    
    Args:
        workspace_id: Workspace identifier
        file: File to upload
        file_id: Optional custom file ID
        current_user: Authenticated user
    
    Returns:
        Upload confirmation with file details
    """
    try:
        # Validate file size
        await validate_file_size_dependency(file)
        
        # Generate file ID if not provided
        if not file_id:
            file_id = str(uuid.uuid4())
        
        # Create workspace directory
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Save file locally
        file_path = os.path.join(workspace_dir, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Store file metadata
        file_info = {
            "file_id": file_id,
            "filename": file.filename,
            "workspace_id": workspace_id,
            "status": "uploaded",
            "storage_path": file_path,
            "storage_type": "local",
            "file_size": file_size,
            "upload_time": datetime.now().isoformat(),
            "user_id": current_user.get("user_id", "unknown")
        }
        
        # Save metadata
        metadata_path = os.path.join(workspace_dir, f"{file_id}_metadata.json")
        import json
        with open(metadata_path, 'w') as f:
            json.dump(file_info, f, indent=2)
        
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "filename": file.filename,
                "status": "uploaded",
                "message": "File uploaded successfully and ready for Gemini processing",
                "details": {
                    "file_size_bytes": file_size,
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "storage_path": file_path,
                    "workspace_id": workspace_id
                }
            }
        )
        
    except Exception as e:
        print(f"File upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )

@router.get("/upload/status/{file_id}")
async def get_upload_status(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get the status of an uploaded file.
    """
    try:
        # Check if file exists
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        file_path = None
        
        # Look for the file in workspace directory
        if os.path.exists(workspace_dir):
            for filename in os.listdir(workspace_dir):
                if filename.startswith(file_id):
                    file_path = os.path.join(workspace_dir, filename)
                    break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Get file info
        file_size = os.path.getsize(file_path)
        upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
        
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "workspace_id": workspace_id,
                "status": "uploaded",
                "file_info": {
                    "file_id": file_id,
                    "filename": os.path.basename(file_path).replace(f"{file_id}_", "", 1),
                    "workspace_id": workspace_id,
                    "status": "stored",
                    "storage_path": file_path,
                    "storage_type": "local",
                    "file_size": file_size,
                    "upload_time": upload_time
                },
                "last_checked": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to get upload status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get upload status: {str(e)}"
        )

@router.delete("/upload/{file_id}")
async def delete_uploaded_file(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Delete an uploaded file.
    """
    try:
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        
        # Find and delete the file
        deleted_files = []
        if os.path.exists(workspace_dir):
            for filename in os.listdir(workspace_dir):
                if filename.startswith(file_id):
                    file_path = os.path.join(workspace_dir, filename)
                    try:
                        os.remove(file_path)
                        deleted_files.append(filename)
                    except Exception as e:
                        print(f"Failed to delete {filename}: {e}")
        
        if not deleted_files:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "workspace_id": workspace_id,
                "status": "deleted",
                "message": f"Deleted {len(deleted_files)} file(s)",
                "deleted_files": deleted_files,
                "deleted_at": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to delete file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.get("/uploads/{workspace_id}")
async def list_workspace_uploads(
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    List all uploaded files in a workspace.
    """
    try:
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        
        if not os.path.exists(workspace_dir):
            return JSONResponse(
                status_code=200,
                content={
                    "workspace_id": workspace_id,
                    "files": [],
                    "total_files": 0,
                    "retrieved_at": datetime.now().isoformat()
                }
            )
        
        files = []
        for filename in os.listdir(workspace_dir):
            if filename.endswith('_metadata.json'):
                continue
                
            file_path = os.path.join(workspace_dir, filename)
            if os.path.isfile(file_path):
                # Extract file_id and original filename
                parts = filename.split('_', 1)
                if len(parts) == 2:
                    file_id, original_filename = parts
                    
                    file_info = {
                        "file_id": file_id,
                        "filename": original_filename,
                        "workspace_id": workspace_id,
                        "storage_path": file_path,
                        "file_size": os.path.getsize(file_path),
                        "upload_time": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                        "storage_type": "local"
                    }
                    files.append(file_info)
        
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
        print(f"Failed to list workspace uploads: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list workspace uploads: {str(e)}"
        )
