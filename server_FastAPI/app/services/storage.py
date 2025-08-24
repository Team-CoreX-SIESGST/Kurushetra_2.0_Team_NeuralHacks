"""
Storage service for OmniSearch AI.
Handles file storage, retrieval, and management.
"""

import os
import uuid
import shutil
from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import json
from app.settings import settings

class StorageService:
    """Service for managing file storage and retrieval."""
    
    def __init__(self):
        self.storage_type = getattr(settings, 'storage_type', 'local')  # 'local' or 's3'
        self.local_storage_path = "data/uploads"
        self.s3_client = None
        self.s3_bucket = getattr(settings, 's3_bucket', 'omnisea-uploads')
        
        # Ensure local storage directory exists
        if self.storage_type == 'local':
            os.makedirs(self.local_storage_path, exist_ok=True)
        
        # Initialize S3 client if needed
        if self.storage_type == 's3':
            self._initialize_s3()
    
    def _initialize_s3(self):
        """Initialize S3 client."""
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=getattr(settings, 's3_endpoint', None),
                aws_access_key_id=getattr(settings, 's3_access_key', None),
                aws_secret_access_key=getattr(settings, 's3_secret_key', None),
                region_name='us-east-1'  # Default region
            )
            print("S3 client initialized successfully")
        except Exception as e:
            print(f"Failed to initialize S3 client: {e}")
            # Fallback to local storage
            self.storage_type = 'local'
            os.makedirs(self.local_storage_path, exist_ok=True)
    
    async def store_file(self, file: BinaryIO, filename: str, workspace_id: str, file_id: str = None) -> Dict[str, Any]:
        """Store a file in the configured storage system."""
        try:
            if not file_id:
                file_id = str(uuid.uuid4())
            
            # Generate storage path
            storage_path = self._generate_storage_path(workspace_id, file_id, filename)
            
            if self.storage_type == 's3':
                return await self._store_file_s3(file, storage_path, filename, workspace_id, file_id)
            else:
                return await self._store_file_local(file, storage_path, filename, workspace_id, file_id)
                
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
    
    async def _store_file_s3(self, file: BinaryIO, storage_path: str, filename: str, workspace_id: str, file_id: str) -> Dict[str, Any]:
        """Store file in S3."""
        try:
            file.seek(0)
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file,
                self.s3_bucket,
                storage_path,
                ExtraArgs={
                    'ContentType': self._get_content_type(filename),
                    'Metadata': {
                        'workspace_id': workspace_id,
                        'file_id': file_id,
                        'original_filename': filename,
                        'upload_time': datetime.now().isoformat()
                    }
                }
            )
            
            # Generate presigned URL for access
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.s3_bucket, 'Key': storage_path},
                ExpiresIn=3600  # 1 hour
            )
            
            return {
                'file_id': file_id,
                'filename': filename,
                'workspace_id': workspace_id,
                'status': 'stored',
                'storage_path': storage_path,
                'storage_type': 's3',
                'bucket': self.s3_bucket,
                'presigned_url': presigned_url,
                'storage_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"S3 storage failed: {e}")
            raise
    
    async def _store_file_local(self, file: BinaryIO, storage_path: str, filename: str, workspace_id: str, file_id: str) -> Dict[str, Any]:
        """Store file locally."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            
            # Copy file to storage location
            with open(storage_path, 'wb') as f:
                shutil.copyfileobj(file, f)
            
            return {
                'file_id': file_id,
                'filename': filename,
                'workspace_id': workspace_id,
                'status': 'stored',
                'storage_path': storage_path,
                'storage_type': 'local',
                'file_size': os.path.getsize(storage_path),
                'storage_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Local storage failed: {e}")
            raise
    
    def _generate_storage_path(self, workspace_id: str, file_id: str, filename: str) -> str:
        """Generate storage path for file."""
        file_extension = os.path.splitext(filename)[1]
        return f"{workspace_id}/{file_id}{file_extension}"
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension."""
        extension = os.path.splitext(filename)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.xml': 'application/xml'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    async def retrieve_file(self, file_id: str, workspace_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """Retrieve file information and generate access URL."""
        try:
            storage_path = self._generate_storage_path(workspace_id, file_id, filename)
            
            if self.storage_type == 's3':
                return await self._retrieve_file_s3(storage_path, file_id, workspace_id, filename)
            else:
                return await self._retrieve_file_local(storage_path, file_id, workspace_id, filename)
                
        except Exception as e:
            print(f"File retrieval failed: {e}")
            return None
    
    async def _retrieve_file_s3(self, storage_path: str, file_id: str, workspace_id: str, filename: str) -> Dict[str, Any]:
        """Retrieve file information from S3."""
        try:
            # Check if file exists
            self.s3_client.head_object(Bucket=self.s3_bucket, Key=storage_path)
            
            # Generate presigned URL
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.s3_bucket, 'Key': storage_path},
                ExpiresIn=3600
            )
            
            return {
                'file_id': file_id,
                'filename': filename,
                'workspace_id': workspace_id,
                'storage_path': storage_path,
                'storage_type': 's3',
                'access_url': presigned_url,
                'retrieval_time': datetime.now().isoformat()
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"File not found in S3: {storage_path}")
                return None
            else:
                raise
    
    async def _retrieve_file_local(self, storage_path: str, file_id: str, workspace_id: str, filename: str) -> Dict[str, Any]:
        """Retrieve file information from local storage."""
        try:
            if not os.path.exists(storage_path):
                print(f"File not found locally: {storage_path}")
                return None
            
            file_stats = os.stat(storage_path)
            
            return {
                'file_id': file_id,
                'filename': filename,
                'workspace_id': workspace_id,
                'storage_path': storage_path,
                'storage_type': 'local',
                'file_size': file_stats.st_size,
                'created_time': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                'retrieval_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Local file retrieval failed: {e}")
            return None
    
    async def delete_file(self, file_id: str, workspace_id: str, filename: str) -> bool:
        """Delete a file from storage."""
        try:
            storage_path = self._generate_storage_path(workspace_id, file_id, filename)
            
            if self.storage_type == 's3':
                return await self._delete_file_s3(storage_path)
            else:
                return await self._delete_file_local(storage_path)
                
        except Exception as e:
            print(f"File deletion failed: {e}")
            return False
    
    async def _delete_file_s3(self, storage_path: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=storage_path)
            return True
        except Exception as e:
            print(f"S3 deletion failed: {e}")
            return False
    
    async def _delete_file_local(self, storage_path: str) -> bool:
        """Delete file from local storage."""
        try:
            if os.path.exists(storage_path):
                os.remove(storage_path)
                return True
            return False
        except Exception as e:
            print(f"Local deletion failed: {e}")
            return False
    
    async def list_workspace_files(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all files in a workspace."""
        try:
            if self.storage_type == 's3':
                return await self._list_workspace_files_s3(workspace_id)
            else:
                return await self._list_workspace_files_local(workspace_id)
                
        except Exception as e:
            print(f"File listing failed: {e}")
            return []
    
    async def _list_workspace_files_s3(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List workspace files in S3."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=f"{workspace_id}/"
            )
            
            files = []
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('/'):  # Skip directories
                    continue
                
                # Extract file info from key
                key_parts = obj['Key'].split('/')
                if len(key_parts) >= 2:
                    file_id = key_parts[1].split('.')[0]
                    extension = os.path.splitext(obj['Key'])[1]
                    
                    files.append({
                        'file_id': file_id,
                        'filename': f"{file_id}{extension}",
                        'workspace_id': workspace_id,
                        'storage_path': obj['Key'],
                        'file_size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'storage_type': 's3'
                    })
            
            return files
            
        except Exception as e:
            print(f"S3 file listing failed: {e}")
            return []
    
    async def _list_workspace_files_local(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List workspace files in local storage."""
        try:
            workspace_path = os.path.join(self.local_storage_path, workspace_id)
            
            if not os.path.exists(workspace_path):
                return []
            
            files = []
            for filename in os.listdir(workspace_path):
                file_path = os.path.join(workspace_path, filename)
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    file_id = filename.split('.')[0]
                    extension = os.path.splitext(filename)[1]
                    
                    files.append({
                        'file_id': file_id,
                        'filename': filename,
                        'workspace_id': workspace_id,
                        'storage_path': file_path,
                        'file_size': file_stats.st_size,
                        'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        'storage_type': 'local'
                    })
            
            return files
            
        except Exception as e:
            print(f"Local file listing failed: {e}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage system statistics."""
        return {
            'storage_type': self.storage_type,
            'local_storage_path': self.local_storage_path if self.storage_type == 'local' else None,
            's3_bucket': self.s3_bucket if self.storage_type == 's3' else None,
            's3_client_initialized': self.s3_client is not None if self.storage_type == 's3' else None
        }
