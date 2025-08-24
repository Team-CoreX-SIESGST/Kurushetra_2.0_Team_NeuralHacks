#!/usr/bin/env python3
"""
Test script for OmniSearch AI API endpoints
"""

import requests
import json
import io

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_files_list():
    """Test files listing endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/v1/files", params={"workspace_id": "test-workspace"})
        print(f"✅ Files list: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Files list failed: {e}")
        return False

def test_upload():
    """Test file upload endpoint"""
    try:
        # Create a simple text file
        test_content = "This is a test document for OmniSearch AI. It contains sample text for testing the upload and search functionality."
        file_obj = io.StringIO(test_content)
        
        files = {"file": ("test.txt", file_obj, "text/plain")}
        data = {"workspace_id": "test-workspace"}
        
        response = requests.post("http://localhost:8000/api/v1/upload", files=files, data=data)
        print(f"✅ Upload test: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text}")
        else:
            print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

def test_search():
    """Test search endpoint"""
    try:
        payload = {
            "workspace_id": "test-workspace",
            "query": "test document",
            "top_k": 5,
            "include_web": False,
            "rerank": False,
            "summarize": True
        }
        
        response = requests.post("http://localhost:8000/api/v1/search", json=payload)
        print(f"✅ Search test: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text}")
        else:
            result = response.json()
            print(f"   Answer: {result.get('answer', 'No answer')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def main():
    print("🧪 Testing OmniSearch AI API endpoints")
    print("=" * 50)
    
    # Test endpoints
    results = []
    results.append(test_health())
    results.append(test_files_list())
    results.append(test_upload())
    results.append(test_search())
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
