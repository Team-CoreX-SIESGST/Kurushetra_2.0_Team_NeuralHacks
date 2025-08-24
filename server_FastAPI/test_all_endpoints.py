#!/usr/bin/env python3
"""
Comprehensive FastAPI Endpoint Testing Script
Tests all endpoints in the OmniSearch AI API
"""

import requests
import json
import time
import os
from pathlib import Path
import io

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api"
V1_BASE = f"{BASE_URL}/api/v1"

def print_test_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_result(test_name, status_code, response_data=None, error=None):
    if error:
        print(f"❌ {test_name}: {error}")
    else:
        status_icon = "✅" if 200 <= status_code < 300 else "⚠️" if status_code == 401 or status_code == 403 else "❌"
        print(f"{status_icon} {test_name}: {status_code}")
        if response_data and len(str(response_data)) < 200:
            print(f"   Response: {response_data}")

def create_test_file():
    """Create a test text file for upload testing"""
    content = """This is a test document for OmniSearch AI testing.
    
    It contains sample text that can be processed by the AI system.
    Key topics include:
    - Artificial Intelligence
    - Document Processing  
    - Machine Learning
    - Text Analysis
    
    This file should be suitable for testing document upload, 
    processing, and AI-powered analysis features."""
    
    test_file_path = "test_document.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return test_file_path

def test_core_endpoints():
    """Test core system endpoints"""
    print_test_header("CORE SYSTEM ENDPOINTS")
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print_result("Health Check", response.status_code, response.json())
    except Exception as e:
        print_result("Health Check", 0, error=str(e))
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print_result("Root Endpoint", response.status_code, response.json())
    except Exception as e:
        print_result("Root Endpoint", 0, error=str(e))
    
    # Test API docs (should return HTML)
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print_result("API Docs", response.status_code, "HTML Documentation Page")
    except Exception as e:
        print_result("API Docs", 0, error=str(e))

def test_user_endpoints():
    """Test user authentication endpoints"""
    print_test_header("USER AUTHENTICATION ENDPOINTS")
    
    # Test user test endpoint
    try:
        response = requests.get(f"{API_BASE}/test", timeout=5)
        print_result("User Test Route", response.status_code, response.json())
    except Exception as e:
        print_result("User Test Route", 0, error=str(e))
    
    # Test user registration (without auth - should work)
    try:
        form_data = {
            'name': 'Test User',
            'phone': '1234567890',
            'pin': 'test123',
            'role': 'user'
        }
        response = requests.post(f"{API_BASE}/register", data=form_data, timeout=10)
        print_result("User Registration", response.status_code, 
                    response.json() if response.headers.get('content-type', '').startswith('application/json') 
                    else "Non-JSON response")
    except Exception as e:
        print_result("User Registration", 0, error=str(e))
    
    # Test user login
    try:
        form_data = {
            'phone': '1234567890',
            'pin': 'test123'
        }
        response = requests.post(f"{API_BASE}/login", data=form_data, timeout=10)
        print_result("User Login", response.status_code,
                    response.json() if response.headers.get('content-type', '').startswith('application/json') 
                    else "Non-JSON response")
    except Exception as e:
        print_result("User Login", 0, error=str(e))

def test_file_endpoints():
    """Test file upload and management endpoints"""
    print_test_header("FILE UPLOAD & MANAGEMENT ENDPOINTS")
    
    # Create test file
    test_file_path = create_test_file()
    workspace_id = "test_workspace"
    
    # Test file upload (without auth - should fail or work depending on middleware)
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {'workspace_id': workspace_id}
            response = requests.post(f"{V1_BASE}/upload", files=files, data=data, timeout=30)
        print_result("File Upload", response.status_code,
                    response.json() if response.headers.get('content-type', '').startswith('application/json') 
                    else "Non-JSON response")
        
        # If upload succeeded, test other file endpoints
        if response.status_code == 200:
            response_data = response.json()
            if 'file_id' in response_data:
                file_id = response_data['file_id']
                
                # Test upload status
                try:
                    response = requests.get(f"{V1_BASE}/upload/status/{file_id}?workspace_id={workspace_id}", timeout=10)
                    print_result("Upload Status", response.status_code, 
                                response.json() if response.headers.get('content-type', '').startswith('application/json') 
                                else "Non-JSON response")
                except Exception as e:
                    print_result("Upload Status", 0, error=str(e))
                
                # Test file info
                try:
                    response = requests.get(f"{V1_BASE}/file/{file_id}?workspace_id={workspace_id}", timeout=10)
                    print_result("File Info", response.status_code,
                                response.json() if response.headers.get('content-type', '').startswith('application/json') 
                                else "Non-JSON response")
                except Exception as e:
                    print_result("File Info", 0, error=str(e))
                
                # Test file metadata
                try:
                    response = requests.get(f"{V1_BASE}/file/{file_id}/metadata?workspace_id={workspace_id}", timeout=10)
                    print_result("File Metadata", response.status_code,
                                response.json() if response.headers.get('content-type', '').startswith('application/json') 
                                else "Non-JSON response")
                except Exception as e:
                    print_result("File Metadata", 0, error=str(e))
    
    except Exception as e:
        print_result("File Upload", 0, error=str(e))
    
    # Clean up
    try:
        os.remove(test_file_path)
    except:
        pass

def test_search_endpoints():
    """Test AI search endpoints"""
    print_test_header("AI SEARCH ENDPOINTS")
    
    workspace_id = "test_workspace"
    test_query = "What is artificial intelligence?"
    
    # Test simple search
    try:
        params = {
            'workspace_id': workspace_id,
            'query': test_query,
            'top_k': 5
        }
        response = requests.get(f"{V1_BASE}/search/simple", params=params, timeout=30)
        print_result("Simple Search", response.status_code,
                    response.json() if response.headers.get('content-type', '').startswith('application/json') 
                    else "Non-JSON response")
    except Exception as e:
        print_result("Simple Search", 0, error=str(e))
    
    # Test advanced search
    try:
        search_data = {
            "workspace_id": workspace_id,
            "query": test_query,
            "top_k": 5,
            "include_web": True,
            "summarize": True
        }
        response = requests.post(f"{V1_BASE}/search", json=search_data, timeout=60)
        print_result("Advanced Search", response.status_code,
                    response.json() if response.headers.get('content-type', '').startswith('application/json') 
                    else "Non-JSON response")
    except Exception as e:
        print_result("Advanced Search", 0, error=str(e))
    
    # Test search stats
    try:
        response = requests.get(f"{V1_BASE}/search/stats/{workspace_id}", timeout=10)
        print_result("Search Stats", response.status_code,
                    response.json() if response.headers.get('content-type', '').startswith('application/json') 
                    else "Non-JSON response")
    except Exception as e:
        print_result("Search Stats", 0, error=str(e))

def test_document_processing_endpoints():
    """Test enhanced document processing endpoints"""
    print_test_header("ENHANCED DOCUMENT PROCESSING ENDPOINTS")
    
    # Create test file
    test_file_path = create_test_file()
    
    # Test single document processing
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {'workspace_id': 'test_workspace'}
            response = requests.post(f"{V1_BASE}/enhanced-documents/process/single", 
                                   files=files, data=data, timeout=60)
        print_result("Single Document Processing", response.status_code,
                    "Processing completed" if response.status_code == 200 else 
                    (response.json() if response.headers.get('content-type', '').startswith('application/json') 
                     else "Non-JSON response"))
    except Exception as e:
        print_result("Single Document Processing", 0, error=str(e))
    
    # Test document to JSON conversion
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            response = requests.post(f"{V1_BASE}/enhanced-documents/convert/json", 
                                   files=files, timeout=30)
        print_result("Document to JSON", response.status_code,
                    "Conversion completed" if response.status_code == 200 else
                    (response.json() if response.headers.get('content-type', '').startswith('application/json') 
                     else "Non-JSON response"))
    except Exception as e:
        print_result("Document to JSON", 0, error=str(e))
    
    # Test basic summarization
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            response = requests.post(f"{V1_BASE}/enhanced-documents/summarize/basic", 
                                   files=files, timeout=60)
        print_result("Basic Summarization", response.status_code,
                    "Summary generated" if response.status_code == 200 else
                    (response.json() if response.headers.get('content-type', '').startswith('application/json') 
                     else "Non-JSON response"))
    except Exception as e:
        print_result("Basic Summarization", 0, error=str(e))
    
    # Test search tag generation
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            response = requests.post(f"{V1_BASE}/enhanced-documents/tags/generate", 
                                   files=files, timeout=30)
        print_result("Search Tag Generation", response.status_code,
                    "Tags generated" if response.status_code == 200 else
                    (response.json() if response.headers.get('content-type', '').startswith('application/json') 
                     else "Non-JSON response"))
    except Exception as e:
        print_result("Search Tag Generation", 0, error=str(e))
    
    # Clean up
    try:
        os.remove(test_file_path)
    except:
        pass

def main():
    """Main testing function"""
    print("🚀 OmniSearch AI API - Comprehensive Endpoint Testing")
    print("="*60)
    print(f"Testing server at: {BASE_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait for server to be ready
    print("\n⏳ Waiting for server to be ready...")
    for i in range(5):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("⚠️  Server may not be ready, continuing with tests...")
    
    # Run all tests
    test_core_endpoints()
    test_user_endpoints()
    test_file_endpoints()
    test_search_endpoints()
    test_document_processing_endpoints()
    
    print(f"\n{'='*60}")
    print("🎯 TESTING COMPLETE!")
    print(f"{'='*60}")
    print("\n📋 Summary:")
    print("✅ = Success (200-299)")
    print("⚠️  = Auth/Permission issue (401, 403)")
    print("❌ = Error (400+, connection issues)")
    print("\n💡 Note: Some endpoints require authentication and may show ⚠️  or ❌")
    print("   This is expected behavior for protected endpoints.")

if __name__ == "__main__":
    main()
