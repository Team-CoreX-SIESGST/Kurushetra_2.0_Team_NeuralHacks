"""
Ingest service for OmniSearch AI.
Handles file processing, chunking, and preparation for indexing.
"""

import os
import uuid
from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime
import PyPDF2
import docx
import json
from app.services.embeddings import EmbeddingsService
from app.services.vectordb import VectorDBService

class IngestService:
    """Service for ingesting and processing files."""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # overlap between chunks
        self.embeddings_service = EmbeddingsService()
    
    async def process_file(self, file: BinaryIO, filename: str, workspace_id: str, file_id: str = None) -> Dict[str, Any]:
        """Process an uploaded file and prepare it for indexing."""
        try:
            if not file_id:
                file_id = str(uuid.uuid4())
            
            # Validate file format
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Extract text content
            text_content = await self._extract_text(file, file_extension)
            
            # Chunk the text
            chunks = self._create_chunks(text_content)
            
            # Generate embeddings for chunks
            await self.embeddings_service.initialize()
            chunk_embeddings = self.embeddings_service.generate_embeddings([chunk['text'] for chunk in chunks])
            
            # Prepare metadata for each chunk
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    'id': f"{file_id}_chunk_{i}",
                    'file_id': file_id,
                    'filename': filename,
                    'chunk_index': i,
                    'text': chunk['text'],
                    'page': chunk.get('page', 1),
                    'start_char': chunk['start_char'],
                    'end_char': chunk['end_char'],
                    'chunk_type': 'text',
                    'timestamp': datetime.now().isoformat()
                }
                chunk_metadata.append(metadata)
            
            # Store in vector database
            vector_db = VectorDBService(workspace_id)
            await vector_db.initialize(self.embeddings_service.get_embedding_dimension())
            
            success = vector_db.add_vectors(chunk_embeddings, chunk_metadata)
            
            if not success:
                raise RuntimeError("Failed to store vectors in database")
            
            # Return processing results
            return {
                'file_id': file_id,
                'filename': filename,
                'workspace_id': workspace_id,
                'status': 'processed',
                'chunks_created': len(chunks),
                'total_characters': len(text_content),
                'processing_time': datetime.now().isoformat(),
                'vector_count': vector_db.get_vector_count()
            }
            
        except Exception as e:
            print(f"File processing failed: {e}")
            return {
                'file_id': file_id or str(uuid.uuid4()),
                'filename': filename,
                'workspace_id': workspace_id,
                'status': 'error',
                'error': str(e),
                'processing_time': datetime.now().isoformat()
            }
    
    async def _extract_text(self, file: BinaryIO, file_extension: str) -> str:
        """Extract text content from different file formats."""
        try:
            if file_extension == '.pdf':
                return await self._extract_pdf_text(file)
            elif file_extension == '.docx':
                return await self._extract_docx_text(file)
            elif file_extension == '.txt':
                return await self._extract_txt_text(file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            print(f"Text extraction failed: {e}")
            raise
    
    async def _extract_pdf_text(self, file: BinaryIO) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            return text_content.strip()
            
        except Exception as e:
            print(f"PDF text extraction failed: {e}")
            raise
    
    async def _extract_docx_text(self, file: BinaryIO) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file)
            text_content = ""
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content += paragraph.text + "\n"
            
            return text_content.strip()
            
        except Exception as e:
            print(f"DOCX text extraction failed: {e}")
            raise
    
    async def _extract_txt_text(self, file: BinaryIO) -> str:
        """Extract text from TXT file."""
        try:
            file.seek(0)
            content = file.read()
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use latin-1 with error handling
            return content.decode('latin-1', errors='ignore')
            
        except Exception as e:
            print(f"TXT text extraction failed: {e}")
            raise
    
    def _create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create overlapping chunks from text content."""
        chunks = []
        
        if len(text) <= self.chunk_size:
            chunks.append({
                'text': text,
                'start_char': 0,
                'end_char': len(text),
                'page': 1
            })
            return chunks
        
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_endings = ['.', '!', '?', '\n\n']
                for ending in sentence_endings:
                    last_ending = text.rfind(ending, start, end)
                    if last_ending > start:
                        end = last_ending + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'start_char': start,
                    'end_char': end,
                    'page': chunk_index + 1
                })
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
            
            chunk_index += 1
        
        return chunks
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get statistics about a file before processing."""
        try:
            if not os.path.exists(file_path):
                return {'error': 'File not found'}
            
            file_size = os.path.getsize(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Estimate chunk count
            estimated_chunks = max(1, file_size // (self.chunk_size * 2))  # Rough estimate
            
            return {
                'file_path': file_path,
                'file_size': file_size,
                'file_extension': file_extension,
                'supported_format': file_extension in self.supported_formats,
                'estimated_chunks': estimated_chunks,
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.supported_formats.copy()
    
    def update_chunking_parameters(self, chunk_size: int = None, chunk_overlap: int = None):
        """Update chunking parameters."""
        if chunk_size is not None:
            self.chunk_size = max(100, chunk_size)  # Minimum chunk size
        
        if chunk_overlap is not None:
            self.chunk_overlap = max(0, min(self.chunk_size // 2, chunk_overlap))  # Reasonable overlap
