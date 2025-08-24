"""
Tests for search response shape validation.
"""

import pytest
import json
from typing import Dict, Any, List
from app.api.v1.search import SearchRequest, SearchResponse

class TestSearchRequest:
    """Test cases for SearchRequest model."""
    
    def test_search_request_required_fields(self):
        """Test SearchRequest with required fields only."""
        request = SearchRequest(
            workspace_id="workspace-123",
            query="Test query"
        )
        
        assert request.workspace_id == "workspace-123"
        assert request.query == "Test query"
        assert request.top_k == 10  # Default value
        assert request.include_web == True  # Default value
        assert request.rerank == True  # Default value
        assert request.summarize == True  # Default value
    
    def test_search_request_all_fields(self):
        """Test SearchRequest with all fields."""
        request = SearchRequest(
            workspace_id="workspace-123",
            query="Test query",
            top_k=5,
            include_web=False,
            rerank=False,
            summarize=False
        )
        
        assert request.workspace_id == "workspace-123"
        assert request.query == "Test query"
        assert request.top_k == 5
        assert request.include_web == False
        assert request.rerank == False
        assert request.summarize == False
    
    def test_search_request_validation(self):
        """Test SearchRequest validation."""
        # Valid request
        request = SearchRequest(
            workspace_id="workspace-123",
            query="Test query"
        )
        assert request is not None
        
        # Test with empty query (should raise validation error)
        with pytest.raises(ValueError):
            SearchRequest(
                workspace_id="workspace-123",
                query=""
            )

class TestSearchResponse:
    """Test cases for SearchResponse model."""
    
    def test_search_response_required_fields(self):
        """Test SearchResponse with required fields only."""
        response = SearchResponse(
            answer="Test answer",
            confidence=0.8,
            sources=[],
            raw_chunks=[],
            processing_time=1.5,
            metadata={}
        )
        
        assert response.answer == "Test answer"
        assert response.confidence == 0.8
        assert response.sources == []
        assert response.raw_chunks == []
        assert response.processing_time == 1.5
        assert response.metadata == {}
    
    def test_search_response_with_sources(self):
        """Test SearchResponse with sources."""
        sources = [
            {
                "file_id": "file-123",
                "filename": "test.pdf",
                "page": 1,
                "snippet": "Test snippet...",
                "score": 0.9,
                "url": ""
            }
        ]
        
        response = SearchResponse(
            answer="Test answer with sources",
            confidence=0.9,
            sources=sources,
            raw_chunks=[],
            processing_time=2.0,
            metadata={"intent": "research_longform"}
        )
        
        assert len(response.sources) == 1
        assert response.sources[0]["file_id"] == "file-123"
        assert response.sources[0]["filename"] == "test.pdf"
    
    def test_search_response_with_raw_chunks(self):
        """Test SearchResponse with raw chunks."""
        raw_chunks = [
            {
                "id": "chunk-1",
                "text": "Chunk text 1",
                "score": 0.85
            },
            {
                "id": "chunk-2",
                "text": "Chunk text 2",
                "score": 0.75
            }
        ]
        
        response = SearchResponse(
            answer="Test answer with chunks",
            confidence=0.8,
            sources=[],
            raw_chunks=raw_chunks,
            processing_time=1.8,
            metadata={"vector_results": 2}
        )
        
        assert len(response.raw_chunks) == 2
        assert response.raw_chunks[0]["id"] == "chunk-1"
        assert response.raw_chunks[1]["score"] == 0.75

class TestSearchResponseShape:
    """Test cases for search response shape validation."""
    
    def test_insufficient_evidence_response(self):
        """Test response shape for insufficient evidence."""
        response = SearchResponse(
            answer="INSUFFICIENT_EVIDENCE",
            confidence=0.0,
            sources=[],
            raw_chunks=[],
            processing_time=0.5,
            metadata={"search_type": "no_results"}
        )
        
        # Validate response structure
        assert response.answer == "INSUFFICIENT_EVIDENCE"
        assert response.confidence == 0.0
        assert len(response.sources) == 0
        assert len(response.raw_chunks) == 0
        
        # Convert to dict for validation
        response_dict = response.dict()
        assert "answer" in response_dict
        assert "confidence" in response_dict
        assert "sources" in response_dict
        assert "raw_chunks" in response_dict
        assert "processing_time" in response_dict
        assert "metadata" in response_dict
    
    def test_successful_search_response(self):
        """Test response shape for successful search."""
        sources = [
            {
                "file_id": "file-123",
                "filename": "research.pdf",
                "page": 1,
                "snippet": "The research methodology...",
                "score": 0.92,
                "url": ""
            },
            {
                "file_id": "file-456",
                "filename": "analysis.pdf",
                "page": 3,
                "snippet": "Analysis shows that...",
                "score": 0.87,
                "url": ""
            }
        ]
        
        raw_chunks = [
            {
                "id": "chunk-1",
                "text": "The research methodology employed in this study...",
                "score": 0.92
            },
            {
                "id": "chunk-2",
                "text": "Analysis shows that the results are significant...",
                "score": 0.87
            }
        ]
        
        metadata = {
            "intent": "research_longform",
            "model_used": "llama2",
            "search_type": "full_pipeline",
            "vector_results": 2,
            "web_results": 1,
            "reranked": True,
            "summarized": True
        }
        
        response = SearchResponse(
            answer="Based on the research [SRC_1] and analysis [SRC_2], the methodology employed...",
            confidence=0.89,
            sources=sources,
            raw_chunks=raw_chunks,
            processing_time=2.3,
            metadata=metadata
        )
        
        # Validate response structure
        assert response.answer.startswith("Based on the research")
        assert "[SRC_1]" in response.answer
        assert "[SRC_2]" in response.answer
        assert response.confidence > 0.8
        assert len(response.sources) == 2
        assert len(response.raw_chunks) == 2
        
        # Validate sources structure
        for source in response.sources:
            assert "file_id" in source
            assert "filename" in source
            assert "page" in source
            assert "snippet" in source
            assert "score" in source
            assert "url" in source
        
        # Validate raw chunks structure
        for chunk in response.raw_chunks:
            assert "id" in chunk
            assert "text" in chunk
            assert "score" in chunk
        
        # Validate metadata structure
        assert "intent" in response.metadata
        assert "model_used" in response.metadata
        assert "search_type" in response.metadata
        assert "vector_results" in response.metadata
        assert "web_results" in response.metadata
        assert "reranked" in response.metadata
        assert "summarized" in response.metadata
    
    def test_response_serialization(self):
        """Test that responses can be serialized to JSON."""
        response = SearchResponse(
            answer="Test answer",
            confidence=0.8,
            sources=[],
            raw_chunks=[],
            processing_time=1.0,
            metadata={"test": True}
        )
        
        # Convert to dict
        response_dict = response.dict()
        
        # Serialize to JSON
        json_str = json.dumps(response_dict)
        
        # Deserialize back
        deserialized = json.loads(json_str)
        
        # Validate structure
        assert deserialized["answer"] == "Test answer"
        assert deserialized["confidence"] == 0.8
        assert deserialized["sources"] == []
        assert deserialized["raw_chunks"] == []
        assert deserialized["processing_time"] == 1.0
        assert deserialized["metadata"]["test"] == True

class TestSearchResponseValidation:
    """Test cases for search response validation."""
    
    def test_confidence_range_validation(self):
        """Test confidence score range validation."""
        # Valid confidence scores
        valid_confidences = [0.0, 0.5, 1.0]
        for confidence in valid_confidences:
            response = SearchResponse(
                answer="Test answer",
                confidence=confidence,
                sources=[],
                raw_chunks=[],
                processing_time=1.0,
                metadata={}
            )
            assert response.confidence == confidence
        
        # Invalid confidence scores should raise validation error
        invalid_confidences = [-0.1, 1.1, 2.0]
        for confidence in invalid_confidences:
            with pytest.raises(ValueError):
                SearchResponse(
                    answer="Test answer",
                    confidence=confidence,
                    sources=[],
                    raw_chunks=[],
                    processing_time=1.0,
                    metadata={}
                )
    
    def test_processing_time_validation(self):
        """Test processing time validation."""
        # Valid processing times
        valid_times = [0.0, 1.5, 10.0]
        for time in valid_times:
            response = SearchResponse(
                answer="Test answer",
                confidence=0.8,
                sources=[],
                raw_chunks=[],
                processing_time=time,
                metadata={}
            )
            assert response.processing_time == time
        
        # Invalid processing times should raise validation error
        invalid_times = [-1.0, -0.5]
        for time in invalid_times:
            with pytest.raises(ValueError):
                SearchResponse(
                    answer="Test answer",
                    confidence=0.8,
                    sources=[],
                    raw_chunks=[],
                    processing_time=time,
                    metadata={}
                )

if __name__ == "__main__":
    pytest.main([__file__])
