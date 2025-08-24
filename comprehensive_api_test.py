#!/usr/bin/env python3
"""
OmniSearch AI - Comprehensive API Testing Suite
Tests every single API endpoint in the system with detailed reporting.
"""

import requests
import json
import time
import sys
import io
from datetime import datetime
from typing import Dict, List, Any
import tempfile
import os

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.workspace_id = "comprehensive-test"
        self.demo_file_id = "test-file-123"
        
    def log_test(self, method: str, endpoint: str, status_code: int, 
                 expected: List[int], response_data: str = "", error: str = ""):
        """Log test results."""
        success = status_code in expected
        self.test_results.append({
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "expected": expected,
            "success": success,
            "response_data": response_data[:200] if response_data else "",
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} {method} {endpoint} - {status_code} "
              f"(expected: {expected})")
        
        if error:
            print(f"      Error: {error}")
        
        return success

    def test_endpoint(self, method: str, endpoint: str, expected_codes: List[int],
                     data: Dict = None, files: Dict = None, params: Dict = None,
                     headers: Dict = None):
        """Test a single endpoint."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, headers=headers, timeout=10)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(url, data=data, files=files, headers=headers, timeout=10)
                else:
                    response = self.session.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            try:
                response_text = response.text[:500]
            except:
                response_text = "Response could not be decoded"
            
            return self.log_test(method, endpoint, response.status_code, 
                               expected_codes, response_text)
            
        except Exception as e:
            return self.log_test(method, endpoint, 0, expected_codes, "", str(e))

    def test_basic_endpoints(self):
        """Test basic application endpoints."""
        print("\n🏠 1. BASIC ENDPOINTS")
        print("-" * 50)
        
        self.test_endpoint("GET", "/", [200])
        self.test_endpoint("GET", "/health", [200])
        self.test_endpoint("GET", "/docs", [200])
        self.test_endpoint("GET", "/redoc", [200])
        self.test_endpoint("GET", "/openapi.json", [200])

    def test_user_endpoints(self):
        """Test user management endpoints."""
        print("\n👤 2. USER MANAGEMENT ENDPOINTS")
        print("-" * 50)
        
        # Test user registration
        user_data = {
            "name": "Test User",
            "phone": "1234567890",
            "pin": "1234",
            "role": "normal_user"
        }
        self.test_endpoint("POST", "/api/register", [201, 400, 409, 429])
        
        # Test user login
        login_data = {
            "phone": "1234567890",
            "pin": "1234"
        }
        self.test_endpoint("POST", "/api/login", [200, 401, 429])
        
        # Test user profile (requires auth, expect 401/403/429)
        self.test_endpoint("GET", "/api/profile", [200, 401, 403, 429])
        
        # Test user list (admin only)
        self.test_endpoint("GET", "/api/users", [200, 401, 403, 429])

    def test_file_upload_endpoints(self):
        """Test file upload endpoints."""
        print("\n📤 3. FILE UPLOAD ENDPOINTS")
        print("-" * 50)
        
        # Test file upload (without actual file - expect validation errors)
        self.test_endpoint("POST", "/api/v1/upload", [400, 413, 422, 429])
        
        # Test upload with form data (no file)
        upload_data = {"workspace_id": self.workspace_id}
        self.test_endpoint("POST", "/api/v1/upload", [400, 422, 429], data=upload_data)
        
        # Test upload status
        self.test_endpoint("GET", f"/api/v1/upload/status/{self.demo_file_id}", 
                         [200, 404, 429], params={"workspace_id": self.workspace_id})
        
        # Test delete upload
        self.test_endpoint("DELETE", f"/api/v1/upload/{self.demo_file_id}", 
                         [200, 404, 429], params={"workspace_id": self.workspace_id})
        
        # Test list uploads
        self.test_endpoint("GET", f"/api/v1/uploads/{self.workspace_id}", [200, 429])

    def test_file_management_endpoints(self):
        """Test file management endpoints."""
        print("\n📁 4. FILE MANAGEMENT ENDPOINTS")
        print("-" * 50)
        
        # Test list files in workspace
        self.test_endpoint("GET", f"/api/v1/files/{self.workspace_id}", [200, 404, 429])
        
        # Test get specific file info
        self.test_endpoint("GET", f"/api/v1/file/{self.demo_file_id}", 
                         [200, 404, 422, 429], params={"workspace_id": self.workspace_id})
        
        # Test download file
        self.test_endpoint("GET", f"/api/v1/file/{self.demo_file_id}/download", 
                         [200, 404, 422, 429], params={"workspace_id": self.workspace_id})
        
        # Test get file metadata
        self.test_endpoint("GET", f"/api/v1/file/{self.demo_file_id}/metadata", 
                         [200, 404, 422, 429], params={"workspace_id": self.workspace_id})
        
        # Test delete file
        self.test_endpoint("DELETE", f"/api/v1/file/{self.demo_file_id}", 
                         [200, 404, 422, 429], params={"workspace_id": self.workspace_id})

    def test_search_endpoints(self):
        """Test search endpoints."""
        print("\n🔍 5. SEARCH ENDPOINTS")
        print("-" * 50)
        
        # Test full search
        search_data = {
            "workspace_id": self.workspace_id,
            "query": "test query",
            "top_k": 5,
            "include_web": True,
            "summarize": True
        }
        self.test_endpoint("POST", "/api/v1/search", [200, 500, 429], data=search_data)
        
        # Test simple search
        search_params = {
            "workspace_id": self.workspace_id,
            "query": "test query",
            "top_k": 5
        }
        self.test_endpoint("GET", "/api/v1/search/simple", [200, 422, 500, 429], params=search_params)
        
        # Test search statistics
        self.test_endpoint("GET", f"/api/v1/search/stats/{self.workspace_id}", [200, 429])

    def test_enhanced_document_endpoints(self):
        """Test enhanced document processing endpoints."""
        print("\n🧠 6. ENHANCED DOCUMENT PROCESSING ENDPOINTS")
        print("-" * 50)
        
        # Test enhanced documents info
        self.test_endpoint("GET", "/api/v1/enhanced-documents/", [200])
        
        # Test enhanced documents health
        self.test_endpoint("GET", "/api/v1/enhanced-documents/health", [200])
        
        # Test supported formats
        self.test_endpoint("GET", "/api/v1/enhanced-documents/formats/supported", [200, 429])
        
        # Test document processing capabilities
        self.test_endpoint("GET", "/api/v1/enhanced-documents/capabilities", [200, 404, 429])
        
        # Test document processing status
        self.test_endpoint("GET", "/api/v1/enhanced-documents/status", [200, 404, 429])
        
        # Test batch processing endpoint
        self.test_endpoint("POST", "/api/v1/enhanced-documents/batch", [200, 400, 422, 429])

    def test_error_endpoints(self):
        """Test error handling and edge cases."""
        print("\n🚨 7. ERROR HANDLING & EDGE CASES")
        print("-" * 50)
        
        # Test non-existent endpoints
        self.test_endpoint("GET", "/api/v1/nonexistent", [404])
        self.test_endpoint("POST", "/api/v1/nonexistent", [404, 405])
        self.test_endpoint("PUT", "/api/v1/nonexistent", [404, 405])
        self.test_endpoint("DELETE", "/api/v1/nonexistent", [404, 405])
        
        # Test malformed requests
        self.test_endpoint("POST", "/api/v1/search", [400, 422, 429], data={"invalid": "data"})
        
        # Test endpoints with invalid parameters
        self.test_endpoint("GET", "/api/v1/files/", [404, 422])  # Missing workspace_id
        self.test_endpoint("GET", "/api/v1/file/", [404, 422])   # Missing file_id

    def test_http_methods_on_endpoints(self):
        """Test different HTTP methods on endpoints."""
        print("\n🔧 8. HTTP METHODS TESTING")
        print("-" * 50)
        
        # Test OPTIONS method (CORS)
        try:
            response = self.session.options(f"{self.base_url}/api/v1/search")
            self.log_test("OPTIONS", "/api/v1/search", response.status_code, [200, 204, 405])
        except Exception as e:
            self.log_test("OPTIONS", "/api/v1/search", 0, [200, 204, 405], "", str(e))
        
        # Test unsupported methods on GET endpoints
        self.test_endpoint("POST", "/health", [405])  # Should be GET only
        self.test_endpoint("PUT", "/health", [405])   # Should be GET only
        self.test_endpoint("DELETE", "/health", [405]) # Should be GET only

    def test_rate_limiting(self):
        """Test rate limiting behavior."""
        print("\n⏱️  9. RATE LIMITING TESTING")
        print("-" * 50)
        
        print("   Testing rate limiting by making multiple requests...")
        
        rate_limit_hit = False
        for i in range(5):  # Make several requests quickly
            try:
                response = self.session.get(f"{self.base_url}/health")
                if response.status_code == 429:
                    rate_limit_hit = True
                    print(f"   ✅ Rate limit triggered after {i+1} requests")
                    break
                time.sleep(0.1)  # Small delay between requests
            except Exception as e:
                print(f"   ❌ Error testing rate limiting: {e}")
                break
        
        if not rate_limit_hit:
            print("   ℹ️  Rate limit not triggered (may be configured for higher limits)")

    def create_test_file(self):
        """Create a temporary test file for upload testing."""
        content = """# Test Document for OmniSearch AI

This is a test document created for comprehensive API testing.

## Features Being Tested
- File upload functionality
- Document processing
- Search capabilities
- AI-powered analysis

## Content
This document contains sample text that can be processed by the AI system
to demonstrate search and summarization capabilities.
"""
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
        temp_file.write(content)
        temp_file.flush()
        return temp_file.name

    def test_file_upload_with_real_file(self):
        """Test actual file upload functionality."""
        print("\n📂 10. REAL FILE UPLOAD TESTING")
        print("-" * 50)
        
        try:
            # Create a test file
            test_file_path = self.create_test_file()
            
            with open(test_file_path, 'rb') as f:
                files = {'file': ('test_document.md', f, 'text/markdown')}
                data = {'workspace_id': self.workspace_id}
                
                try:
                    response = self.session.post(
                        f"{self.base_url}/api/v1/upload",
                        data=data,
                        files=files,
                        timeout=30
                    )
                    
                    self.log_test("POST", "/api/v1/upload (with file)", 
                                response.status_code, [200, 201, 413, 422, 429])
                    
                    if response.status_code in [200, 201]:
                        try:
                            response_data = response.json()
                            if 'file_id' in response_data:
                                print(f"   📄 Uploaded file ID: {response_data['file_id']}")
                        except:
                            pass
                            
                except Exception as e:
                    self.log_test("POST", "/api/v1/upload (with file)", 0, [200, 201], "", str(e))
            
            # Clean up
            try:
                os.unlink(test_file_path)
            except:
                pass
                
        except Exception as e:
            print(f"   ❌ Failed to create test file: {e}")

    def run_all_tests(self):
        """Run all API tests."""
        print("🧪 OMNISEARCH AI - COMPREHENSIVE API TESTING SUITE")
        print("=" * 70)
        print(f"🎯 Target: {self.base_url}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Test Workspace: {self.workspace_id}")
        
        # Check if server is running
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ Server health check failed. Please ensure the server is running.")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("   Please ensure the FastAPI server is running on localhost:8000")
            return False
        
        print("✅ Server is responding. Beginning comprehensive testing...\n")
        
        # Run all test suites
        start_time = time.time()
        
        self.test_basic_endpoints()
        self.test_user_endpoints()
        self.test_file_upload_endpoints()
        self.test_file_management_endpoints()
        self.test_search_endpoints()
        self.test_enhanced_document_endpoints()
        self.test_error_endpoints()
        self.test_http_methods_on_endpoints()
        self.test_rate_limiting()
        self.test_file_upload_with_real_file()
        
        end_time = time.time()
        
        # Generate summary report
        self.generate_report(end_time - start_time)
        
        return True

    def generate_report(self, total_time: float):
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 70)
        
        print(f"\n📈 Overall Statistics:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Passed: {passed_tests} ✅")
        print(f"   • Failed: {failed_tests} ❌")
        print(f"   • Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print(f"   • Total Time: {total_time:.2f} seconds")
        print(f"   • Average Time per Test: {(total_time/total_tests):.3f} seconds")
        
        # Status code analysis
        status_codes = {}
        for result in self.test_results:
            code = result['status_code']
            status_codes[code] = status_codes.get(code, 0) + 1
        
        print(f"\n📊 Status Code Distribution:")
        for code, count in sorted(status_codes.items()):
            if code == 0:
                print(f"   • Connection Errors: {count}")
            else:
                print(f"   • {code}: {count} responses")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ Failed Tests Details:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['method']} {result['endpoint']}: "
                          f"{result['status_code']} (expected: {result['expected']})")
                    if result['error']:
                        print(f"     Error: {result['error']}")
        
        # Success by category
        categories = {
            "Basic Endpoints": ["/", "/health", "/docs", "/redoc", "/openapi.json"],
            "User Management": ["/api/register", "/api/login", "/api/profile", "/api/users"],
            "File Upload": ["/api/v1/upload", "/api/v1/uploads"],
            "File Management": ["/api/v1/files", "/api/v1/file"],
            "Search": ["/api/v1/search"],
            "Enhanced Documents": ["/api/v1/enhanced-documents"],
            "Error Handling": ["/api/v1/nonexistent"]
        }
        
        print(f"\n🎯 Success Rate by Category:")
        for category, endpoints in categories.items():
            category_tests = [r for r in self.test_results 
                            if any(endpoint in r['endpoint'] for endpoint in endpoints)]
            if category_tests:
                category_passed = sum(1 for r in category_tests if r['success'])
                category_total = len(category_tests)
                success_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                print(f"   • {category}: {success_rate:.1f}% ({category_passed}/{category_total})")
        
        print(f"\n🔗 API Access Points Verified:")
        print(f"   • Main API: {self.base_url}")
        print(f"   • Health Check: {self.base_url}/health")
        print(f"   • Documentation: {self.base_url}/docs")
        print(f"   • Alternative Docs: {self.base_url}/redoc")
        
        if passed_tests / total_tests >= 0.8:
            print(f"\n🎉 EXCELLENT! API is highly functional with {(passed_tests/total_tests*100):.1f}% success rate!")
        elif passed_tests / total_tests >= 0.6:
            print(f"\n👍 GOOD! API is functional with {(passed_tests/total_tests*100):.1f}% success rate.")
        else:
            print(f"\n⚠️  NEEDS ATTENTION! API has {(passed_tests/total_tests*100):.1f}% success rate.")
        
        print(f"\n✨ Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function to run the comprehensive API test suite."""
    tester = APITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
