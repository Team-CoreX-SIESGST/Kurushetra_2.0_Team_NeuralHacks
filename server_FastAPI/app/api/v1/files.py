"""
Files API endpoint for OmniSearch AI.
Simplified Gemini-only file management implementation.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import json
from app.middlewares.auth import verify_token

router = APIRouter(prefix="/api/v1", tags=["files"])

# Local storage path
UPLOAD_DIR = "data/uploads"

@router.get("/file/{file_id}")
async def get_file_info(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get file information and metadata.
    """
    try:
        # Look for file in workspace directory
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        file_path = None
        metadata_path = None
        
        if os.path.exists(workspace_dir):
            for filename in os.listdir(workspace_dir):
                if filename.startswith(file_id):
                    if filename.endswith('_metadata.json'):
                        metadata_path = os.path.join(workspace_dir, filename)
                    else:
                        file_path = os.path.join(workspace_dir, filename)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file info
        file_size = os.path.getsize(file_path)
        upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
        
        # Try to get metadata
        metadata = {}
        if metadata_path and os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            except:
                pass
        
        file_info = {
            "file_id": file_id,
            "filename": os.path.basename(file_path).replace(f"{file_id}_", "", 1),
            "workspace_id": workspace_id,
            "status": "stored",
            "storage_path": file_path,
            "storage_type": "local",
            "file_size": file_size,
            "upload_time": upload_time,
            **metadata
        }
        
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

@router.get("/file/{file_id}/download")
async def download_file(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Download a file.
    """
    try:
        # Look for file in workspace directory
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        file_path = None
        
        if os.path.exists(workspace_dir):
            for filename in os.listdir(workspace_dir):
                if filename.startswith(file_id) and not filename.endswith('_metadata.json'):
                    file_path = os.path.join(workspace_dir, filename)
                    break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file for download
        filename = os.path.basename(file_path).replace(f"{file_id}_", "", 1)
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
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
    """
    try:
        # Look for file in workspace directory
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        file_path = None
        metadata_path = None
        
        if os.path.exists(workspace_dir):
            for filename in os.listdir(workspace_dir):
                if filename.startswith(file_id):
                    if filename.endswith('_metadata.json'):
                        metadata_path = os.path.join(workspace_dir, filename)
                    else:
                        file_path = os.path.join(workspace_dir, filename)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get basic file info
        file_size = os.path.getsize(file_path)
        upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        
        # Try to get stored metadata
        stored_metadata = {}
        if metadata_path and os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    stored_metadata = json.load(f)
            except:
                pass
        
        # Prepare comprehensive metadata
        metadata = {
            "storage_info": {
                "file_id": file_id,
                "filename": os.path.basename(file_path).replace(f"{file_id}_", "", 1),
                "workspace_id": workspace_id,
                "status": "stored",
                "storage_path": file_path,
                "storage_type": "local",
                "file_size": file_size,
                "upload_time": upload_time,
                "modified_time": modified_time
            },
            "file_statistics": {
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "file_extension": os.path.splitext(file_path)[1].lower(),
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK)
            },
            "stored_metadata": stored_metadata,
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

@router.delete("/file/{file_id}")
async def delete_file(
    file_id: str,
    workspace_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Delete a file and its associated data.
    """
    try:
        workspace_dir = os.path.join(UPLOAD_DIR, workspace_id)
        
        # Find and delete the file and metadata
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
        print(f"File listing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File listing failed: {str(e)}"
        )
