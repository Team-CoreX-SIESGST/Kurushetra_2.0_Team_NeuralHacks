#!/usr/bin/env python3
"""
Comprehensive API Testing Script for OmniSearch AI
Tests all endpoints to ensure they're working correctly.
"""

import requests
import json
import time
from datetime import datetime

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Test a single endpoint and return the result."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return False, f"Unsupported method: {method}"
        
        success = response.status_code < 400
        result = f"✅ {description} - Status: {response.status_code}"
        
        if response.status_code == 401:
            result += " (Unauthorized - Expected for protected endpoints)"
        elif response.status_code == 404:
            result += " (Not Found - May be expected for some endpoints)"
        
        return success, result
        
    except requests.exceptions.ConnectionError:
        return False, f"❌ {description} - Connection Error (Server may not be running)"
    except requests.exceptions.Timeout:
        return False, f"❌ {description} - Timeout Error"
    except Exception as e:
        return False, f"❌ {description} - Error: {str(e)}"

def main():
    """Run all API tests."""
    print("🚀 OmniSearch AI - Comprehensive API Testing")
    print("=" * 60)
    print(f"Testing server at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test results tracking
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # 1. Basic Endpoints (No Auth Required)
    print("📋 1. Testing Basic Endpoints")
    print("-" * 40)
    
    basic_endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/docs", "API documentation"),
        ("GET", "/redoc", "Alternative API docs"),
    ]
    
    for method, endpoint, description in basic_endpoints:
        total_tests += 1
        success, result = test_endpoint(method, endpoint, description=description)
        print(result)
        if success:
            passed_tests += 1
        else:
            failed_tests += 1
    
    print()
    
    # 2. Search Endpoints (Auth Required - Will get 401)
    print("🔍 2. Testing Search Endpoints (Auth Required)")
    print("-" * 40)
    
    search_endpoints = [
        ("POST", "/api/v1/search", "Full search with Gemini"),
        ("GET", "/api/v1/search/simple", "Simple search"),
        ("GET", "/api/v1/search/stats/demo-workspace", "Search statistics"),
    ]
    
    for method, endpoint, description in search_endpoints:
        total_tests += 1
        if method == "POST":
            data = {"workspace_id": "demo", "query": "test query", "top_k": 5}
        else:
            data = None
        
        success, result = test_endpoint(method, endpoint, data=data, description=description)
        print(result)
        if success:
            passed_tests += 1
        else:
            failed_tests += 1
    
    print()
    
    # 3. File Management Endpoints (Auth Required - Will get 401)
    print("📁 3. Testing File Management Endpoints (Auth Required)")
    print("-" * 40)
    
    file_endpoints = [
        ("GET", "/api/v1/files/demo-workspace", "List workspace files"),
        ("GET", "/api/v1/file/test-file-id", "Get file info"),
        ("GET", "/api/v1/file/test-file-id/download", "Download file"),
        ("GET", "/api/v1/file/test-file-id/metadata", "Get file metadata"),
    ]
    
    for method, endpoint, description in file_endpoints:
        total_tests += 1
        success, result = test_endpoint(method, endpoint, description=description)
        print(result)
        if success:
            passed_tests += 1
        else:
            failed_tests += 1
    
    print()
    
    # 4. Upload Endpoints (Auth Required - Will get 401)
    print("📤 4. Testing Upload Endpoints (Auth Required)")
    print("-" * 40)
    
    upload_endpoints = [
        ("GET", "/api/v1/uploads/demo-workspace", "List workspace uploads"),
        ("GET", "/api/v1/upload/status/test-file-id", "Get upload status"),
    ]
    
    for method, endpoint, description in upload_endpoints:
        total_tests += 1
        success, result = test_endpoint(method, endpoint, description=description)
        print(result)
        if success:
            passed_tests += 1
        else:
            failed_tests += 1
    
    print()
    
    # 5. Enhanced Document Processing Endpoints (Auth Required - Will get 401)
    print("🧠 5. Testing Enhanced Document Processing (Auth Required)")
    print("-" * 40)
    
    enhanced_endpoints = [
        ("GET", "/api/v1/enhanced-documents/", "Enhanced documents info"),
        ("GET", "/api/v1/enhanced-documents/health", "Enhanced documents health"),
        ("GET", "/api/v1/enhanced-documents/formats/supported", "Supported formats"),
    ]
    
    for method, endpoint, description in enhanced_endpoints:
        total_tests += 1
        success, result = test_endpoint(method, endpoint, description=description)
        print(result)
        if success:
            passed_tests += 1
        else:
            failed_tests += 1
    
    print()
    
    # 6. User Routes (Auth Required - Will get 401)
    print("👤 6. Testing User Routes (Auth Required)")
    print("-" * 40)
    
    user_endpoints = [
        ("GET", "/api/users", "List users"),
        ("GET", "/api/users/profile", "Get user profile"),
    ]
    
    for method, endpoint, description in user_endpoints:
        total_tests += 1
        success, result = test_endpoint(method, endpoint, description=description)
        print(result)
        if success:
            passed_tests += 1
        else:
            failed_tests += 1
    
    print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    if failed_tests == 0:
        print("🎉 All tests passed! The API is working perfectly.")
    else:
        print("⚠️  Some tests failed. This may be expected for protected endpoints.")
        print("   - 401 errors are expected for endpoints requiring authentication")
        print("   - 404 errors may be expected for some endpoints")
    
    print()
    print("🔗 API Documentation: http://127.0.0.1:8000/docs")
    print("🔗 Alternative Docs: http://127.0.0.1:8000/redoc")
    print("🎨 Streamlit Frontend: http://127.0.0.1:8501")

if __name__ == "__main__":
    main()
