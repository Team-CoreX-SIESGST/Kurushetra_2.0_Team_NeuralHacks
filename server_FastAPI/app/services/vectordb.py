"""
Vector database service for OmniSearch AI.
Handles FAISS-based similarity search and storage.
"""

import faiss
import numpy as np
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.config import settings

class VectorDBService:
    """Service for managing vector database operations using FAISS."""
    
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.index = None
        self.metadata = []
        self.index_path = f"data/vectordb/{workspace_id}"
        self.metadata_path = f"{self.index_path}/metadata.json"
        
        # Ensure directory exists
        os.makedirs(self.index_path, exist_ok=True)
    
    async def initialize(self, embedding_dim: int = 384):
        """Initialize the FAISS index."""
        try:
            # Try to load existing index
            if os.path.exists(f"{self.index_path}/index.faiss"):
                self.index = faiss.read_index(f"{self.index_path}/index.faiss")
                self._load_metadata()
                print(f"Loaded existing FAISS index for workspace {self.workspace_id}")
            else:
                # Create new index
                self.index = faiss.IndexFlatIP(embedding_dim)  # Inner product for cosine similarity
                self.metadata = []
                print(f"Created new FAISS index for workspace {self.workspace_id}")
                
        except Exception as e:
            print(f"Failed to initialize vector database: {e}")
            # Create fallback index
            self.index = faiss.IndexFlatIP(embedding_dim)
            self.metadata = []
    
    def add_vectors(self, vectors: np.ndarray, metadata_list: List[Dict[str, Any]]) -> bool:
        """Add vectors and metadata to the database."""
        try:
            if self.index is None:
                raise RuntimeError("Vector database not initialized")
            
            # Add vectors to FAISS index
            self.index.add(vectors)
            
            # Add metadata
            for metadata in metadata_list:
                metadata['vector_id'] = len(self.metadata)
                metadata['timestamp'] = datetime.now().isoformat()
                self.metadata.append(metadata)
            
            # Save index and metadata
            self._save_index()
            self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Failed to add vectors: {e}")
            return False
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            if self.index is None:
                raise RuntimeError("Vector database not initialized")
            
            # Ensure query vector is 2D
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_vector, min(top_k, len(self.metadata)))
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.metadata) and idx >= 0:
                    result = self.metadata[idx].copy()
                    result['score'] = float(score)
                    result['rank'] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def get_vector_count(self) -> int:
        """Get the total number of vectors in the database."""
        if self.index is None:
            return 0
        return self.index.ntotal
    
    def delete_vectors(self, vector_ids: List[int]) -> bool:
        """Delete vectors by their IDs."""
        try:
            if self.index is None:
                raise RuntimeError("Vector database not initialized")
            
            # FAISS doesn't support deletion, so we need to rebuild
            # This is a simplified approach - in production, consider using a different index type
            
            # Get all vectors except the ones to delete
            all_vectors = self.index.reconstruct_n(0, self.index.ntotal)
            keep_indices = [i for i in range(len(self.metadata)) if i not in vector_ids]
            
            if not keep_indices:
                # All vectors deleted, reset index
                self.index = faiss.IndexFlatIP(self.index.d)
                self.metadata = []
            else:
                # Rebuild index with remaining vectors
                new_vectors = all_vectors[keep_indices]
                new_metadata = [self.metadata[i] for i in keep_indices]
                
                self.index = faiss.IndexFlatIP(self.index.d)
                self.index.add(new_vectors)
                self.metadata = new_metadata
            
            # Save updated index and metadata
            self._save_index()
            self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Failed to delete vectors: {e}")
            return False
    
    def _save_index(self):
        """Save the FAISS index to disk."""
        try:
            faiss.write_index(self.index, f"{self.index_path}/index.faiss")
        except Exception as e:
            print(f"Failed to save index: {e}")
    
    def _save_metadata(self):
        """Save metadata to disk."""
        try:
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Failed to save metadata: {e}")
    
    def _load_metadata(self):
        """Load metadata from disk."""
        try:
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
        except Exception as e:
            print(f"Failed to load metadata: {e}")
            self.metadata = []
    
    def get_workspace_stats(self) -> Dict[str, Any]:
        """Get statistics about the workspace."""
        return {
            "workspace_id": self.workspace_id,
            "vector_count": self.get_vector_count(),
            "index_dimension": self.index.d if self.index else 0,
            "last_updated": datetime.now().isoformat()
        }
