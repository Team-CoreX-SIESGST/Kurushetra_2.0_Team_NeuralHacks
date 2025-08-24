#!/usr/bin/env python3
"""
Simple test script for Streamlit frontend components.
This script tests the OmniSearchClient class and basic functionality.
"""

import sys
import os
import requests
from unittest.mock import Mock, patch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import OmniSearchClient

def test_client_initialization():
    """Test OmniSearchClient initialization."""
    print("🧪 Testing client initialization...")
    
    # Test without token
    client = OmniSearchClient("http://localhost:8000", "")
    assert client.base_url == "http://localhost:8000"
    assert client.headers == {}
    
    # Test with token
    client = OmniSearchClient("http://localhost:8000", "test-token")
    assert client.headers == {"Authorization": "Bearer test-token"}
    
    print("✅ Client initialization: PASS")

def test_health_check():
    """Test health check functionality."""
    print("🧪 Testing health check...")
    
    client = OmniSearchClient("http://localhost:8000", "")
    
    # Test with mock successful response
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = client.health_check()
        assert result == True
    
    # Test with mock failed response
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection failed")
        
        result = client.health_check()
        assert result == False
    
    print("✅ Health check: PASS")

def test_upload_file():
    """Test file upload functionality."""
    print("🧪 Testing file upload...")
    
    client = OmniSearchClient("http://localhost:8000", "test-token")
    
    # Mock file object
    mock_file = Mock()
    mock_file.name = "test.pdf"
    
    # Mock successful response
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "file_id": "test-123",
            "message": "File uploaded successfully"
        }
        mock_post.return_value = mock_response
        
        result = client.upload_file(mock_file, "test-workspace", "test-123")
        assert result["success"] == True
        assert result["file_id"] == "test-123"
    
    print("✅ File upload: PASS")

def test_search():
    """Test search functionality."""
    print("🧪 Testing search...")
    
    client = OmniSearchClient("http://localhost:8000", "test-token")
    
    # Mock successful response
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "answer": "This is a test answer",
                "confidence": 0.85,
                "sources": [
                    {"src_id": "SRC_1", "quote": "Test quote", "url_or_file": "test.pdf"}
                ]
            }
        }
        mock_post.return_value = mock_response
        
        result = client.search(
            workspace_id="test-workspace",
            query="What is machine learning?",
            top_k=10,
            include_web=True,
            rerank=True,
            summarize=True
        )
        
        assert result["success"] == True
        assert "answer" in result["data"]
        assert "sources" in result["data"]
    
    print("✅ Search: PASS")

def test_file_operations():
    """Test file management operations."""
    print("🧪 Testing file operations...")
    
    client = OmniSearchClient("http://localhost:8000", "test-token")
    
    # Test list files
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "files": [
                    {"file_id": "file1", "filename": "test1.pdf", "status": "processed"}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = client.list_files("test-workspace")
        assert result["success"] == True
        assert len(result["data"]["files"]) == 1
    
    # Test get file info
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "file_id": "file1",
                "filename": "test1.pdf",
                "status": "processed",
                "chunk_count": 5
            }
        }
        mock_get.return_value = mock_response
        
        result = client.get_file_info("file1", "test-workspace")
        assert result["success"] == True
        assert result["data"]["filename"] == "test1.pdf"
    
    print("✅ File operations: PASS")

def run_all_tests():
    """Run all tests."""
    print("🚀 Running OmniSearch Frontend Tests")
    print("=" * 50)
    
    try:
        test_client_initialization()
        test_health_check()
        test_upload_file()
        test_search()
        test_file_operations()
        
        print("\n🎉 All tests passed!")
        print("✅ Frontend components are working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
