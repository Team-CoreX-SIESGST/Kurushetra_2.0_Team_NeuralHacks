"""
Simplified storage service for OmniSearch AI.
Local file storage only for Gemini processing.
"""

import os
import uuid
import shutil
from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime
import json
from app.settings import settings

class StorageService:
    """Simplified service for managing local file storage."""
    
    def __init__(self):
        self.local_storage_path = "data/uploads"
        
        # Ensure local storage directory exists
        os.makedirs(self.local_storage_path, exist_ok=True)
    
    async def store_file(self, file: BinaryIO, filename: str, workspace_id: str, file_id: str = None) -> Dict[str, Any]:
        """Store a file locally."""
        try:
            if not file_id:
                file_id = str(uuid.uuid4())
            
            # Create workspace directory
            workspace_dir = os.path.join(self.local_storage_path, workspace_id)
            os.makedirs(workspace_dir, exist_ok=True)
            
            # Generate storage path
            storage_path = os.path.join(workspace_dir, f"{file_id}_{filename}")
            
            # Store file locally
            with open(storage_path, 'wb') as buffer:
                shutil.copyfileobj(file, buffer)
            
            # Get file size
            file_size = os.path.getsize(storage_path)
            
            # Store metadata
            metadata = {
                "file_id": file_id,
                "filename": filename,
                "workspace_id": workspace_id,
                "status": "stored",
                "storage_path": storage_path,
                "storage_type": "local",
                "file_size": file_size,
                "storage_time": datetime.now().isoformat()
            }
            
            metadata_path = os.path.join(workspace_dir, f"{file_id}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                'file_id': file_id,
                'filename': filename,
                'workspace_id': workspace_id,
                'status': 'success',
                'storage_path': storage_path,
                'file_size': file_size,
                'storage_time': datetime.now().isoformat()
            }
                
        except Exception as e:
            print(f"File storage failed: {e}")
            return {
                'file_id': file_id or str(uuid.uuid4()),
                'filename': filename,
                'workspace_id': workspace_id,
                'status': 'error',
                'error': str(e),
                'storage_time': datetime.now().isoformat()
            }
    
    async def retrieve_file(self, file_id: str, workspace_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """Retrieve file information."""
        try:
            workspace_dir = os.path.join(self.local_storage_path, workspace_id)
            file_path = os.path.join(workspace_dir, f"{file_id}_{filename}")
            
            if not os.path.exists(file_path):
                return None
            
            file_size = os.path.getsize(file_path)
            upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
            
            return {
                "file_id": file_id,
                "filename": filename,
                "workspace_id": workspace_id,
                "status": "stored",
                "storage_path": file_path,
                "storage_type": "local",
                "file_size": file_size,
                "upload_time": upload_time
            }
            
        except Exception as e:
            print(f"File retrieval failed: {e}")
            return None
    
    async def delete_file(self, file_id: str, workspace_id: str, filename: str) -> bool:
        """Delete a file."""
        try:
            workspace_dir = os.path.join(self.local_storage_path, workspace_id)
            file_path = os.path.join(workspace_dir, f"{file_id}_{filename}")
            metadata_path = os.path.join(workspace_dir, f"{file_id}_metadata.json")
            
            deleted = False
            
            # Delete main file
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted = True
            
            # Delete metadata
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            return deleted
            
        except Exception as e:
            print(f"File deletion failed: {e}")
            return False
    
    async def list_workspace_files(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all files in a workspace."""
        try:
            workspace_dir = os.path.join(self.local_storage_path, workspace_id)
            
            if not os.path.exists(workspace_dir):
                return []
            
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
            
            return files
            
        except Exception as e:
            print(f"File listing failed: {e}")
            return []
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension."""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.rtf': 'application/rtf',
            '.odt': 'application/vnd.oasis.opendocument.text',
            '.csv': 'text/csv'
        }
        return content_types.get(ext, 'application/octet-stream')
