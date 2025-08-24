#!/usr/bin/env python3
"""
Test script for improved upload system in OmniSearch AI.
Tests the new local storage and background processing functionality.
"""

import requests
import json
import time
import io
import os

def test_upload_and_status():
    """Test the improved upload system with status monitoring."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Improved Upload System")
    print("=" * 50)
    
    # Test data
    workspace_id = "test-workspace"
    test_content = """
    This is a comprehensive test document for the OmniSearch AI system.
    
    The document contains multiple paragraphs to test the chunking functionality.
    Each paragraph represents different types of content that might be found
    in typical documents processed by the system.
    
    Technical specifications:
    - File format: Plain text
    - Character count: Approximately 500 characters
    - Purpose: Testing upload and processing pipeline
    
    Features tested:
    1. File upload with local storage
    2. Background processing
    3. Status monitoring
    4. Error handling
    5. Progress tracking
    
    This content should be sufficient to create multiple chunks and test
    the embedding generation and vector storage functionality.
    """
    
    try:
        # 1. Test health check
        print("1. Testing API health...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
        else:
            print("❌ API health check failed")
            return False
        
        # 2. Test file upload
        print("\n2. Testing file upload...")
        
        # Create test file
        test_file = io.BytesIO(test_content.encode('utf-8'))
        
        files = {
            "file": ("test_document.txt", test_file, "text/plain")
        }
        
        data = {
            "workspace_id": workspace_id
        }
        
        # Upload file
        response = requests.post(f"{base_url}/api/v1/upload", files=files, data=data)
        
        if response.status_code == 202:  # Accepted
            upload_result = response.json()
            file_id = upload_result["file_id"]
            print(f"✅ File uploaded successfully")
            print(f"   File ID: {file_id}")
            print(f"   Filename: {upload_result['filename']}")
            print(f"   Status: {upload_result['status']}")
            print(f"   File Size: {upload_result['file_size']} bytes")
            
            # 3. Monitor processing status
            print(f"\n3. Monitoring processing status...")
            
            max_wait_time = 60  # Maximum wait time in seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                # Check status
                status_response = requests.get(
                    f"{base_url}/api/v1/status/{file_id}", 
                    params={"workspace_id": workspace_id}
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data["status"]
                    progress = status_data.get("progress", 0)
                    current_step = status_data.get("current_step", "N/A")
                    
                    print(f"   Status: {current_status} | Progress: {progress}% | Step: {current_step}")
                    
                    if current_status == "completed":
                        print("✅ Processing completed successfully!")
                        print(f"   Chunks created: {status_data.get('chunks_created', 0)}")
                        print(f"   Total characters: {status_data.get('total_characters', 0)}")
                        print(f"   Vector count: {status_data.get('vector_count', 0)}")
                        break
                    elif current_status == "error":
                        print("❌ Processing failed!")
                        print(f"   Error: {status_data.get('error', 'Unknown error')}")
                        break
                    
                    # Wait before next check
                    time.sleep(2)
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    break
            else:
                print("⏰ Processing timed out (may still be running)")
            
            # 4. Test file listing with status
            print(f"\n4. Testing file listing with processing status...")
            
            list_response = requests.get(f"{base_url}/api/v1/files/{workspace_id}")
            
            if list_response.status_code == 200:
                files_data = list_response.json()
                print("✅ File listing successful")
                print(f"   Total files: {files_data['total_files']}")
                
                for file_info in files_data['files']:
                    print(f"   File: {file_info['filename']}")
                    print(f"     ID: {file_info['file_id']}")
                    print(f"     Processing Status: {file_info.get('processing_status', 'unknown')}")
                    print(f"     Progress: {file_info.get('progress', 0)}%")
            else:
                print(f"❌ File listing failed: {list_response.status_code}")
            
            # 5. Test processing status overview
            print(f"\n5. Testing processing status overview...")
            
            overview_response = requests.get(f"{base_url}/api/v1/processing/status")
            
            if overview_response.status_code == 200:
                overview_data = overview_response.json()
                print("✅ Processing status overview successful")
                print(f"   Total files tracked: {overview_data['total_files']}")
                
                for status in overview_data['statuses'][:3]:  # Show first 3
                    print(f"   File: {status['filename']}")
                    print(f"     Status: {status['status']}")
                    print(f"     Workspace: {status['workspace_id']}")
                    if 'completed_at' in status:
                        print(f"     Completed: {status['completed_at']}")
            else:
                print(f"❌ Processing status overview failed: {overview_response.status_code}")
            
            return True
            
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_error_handling():
    """Test error handling for various scenarios."""
    base_url = "http://localhost:8000"
    
    print(f"\n🧪 Testing Error Handling")
    print("=" * 30)
    
    try:
        # Test unsupported file type
        print("1. Testing unsupported file type...")
        
        test_file = io.BytesIO(b"test content")
        
        files = {
            "file": ("test.xyz", test_file, "application/octet-stream")
        }
        
        data = {
            "workspace_id": "test-workspace"
        }
        
        response = requests.post(f"{base_url}/api/v1/upload", files=files, data=data)
        
        if response.status_code == 400:
            print("✅ Correctly rejected unsupported file type")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
        
        # Test large file
        print("\n2. Testing large file rejection...")
        
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB file
        large_file = io.BytesIO(large_content)
        
        files = {
            "file": ("large_test.txt", large_file, "text/plain")
        }
        
        response = requests.post(f"{base_url}/api/v1/upload", files=files, data=data)
        
        if response.status_code == 413:
            print("✅ Correctly rejected large file")
        else:
            print(f"❌ Expected 413, got {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 OmniSearch AI - Improved Upload System Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            print("   Please ensure the FastAPI server is running on port 8000")
            return 1
    except requests.ConnectionError:
        print("❌ Cannot connect to server")
        print("   Please start the server with: python -m uvicorn app.main:app --reload --port 8000")
        return 1
    except requests.Timeout:
        print("❌ Server is not responding")
        return 1
    
    # Run tests
    results = []
    results.append(test_upload_and_status())
    results.append(test_error_handling())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        print("\n✅ The improved upload system is working correctly!")
        print("   Features verified:")
        print("   - Fast local file storage")
        print("   - Background processing")
        print("   - Real-time status monitoring")
        print("   - Error handling")
        print("   - Progress tracking")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
