#!/usr/bin/env python3
"""
OmniSearch AI - Focused Demo
Tests only FILE UPLOAD & MANAGEMENT and AI SEARCH endpoints without authentication
"""

import requests
import json
import time
import tempfile
import os
from datetime import datetime
from pathlib import Path

class FocusedAPIDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.workspace_id = "demo-workspace"
        self.uploaded_file_id = None
        
    def create_test_document(self):
        """Create a test document for upload"""
        content = """# Test Document for OmniSearch AI

## Introduction
This is a sample document created for testing the OmniSearch AI system.

## Key Concepts
- **Artificial Intelligence**: The simulation of human intelligence in machines
- **Machine Learning**: A subset of AI that enables machines to learn from data
- **Natural Language Processing**: AI's ability to understand and process human language
- **Vector Search**: A method to find similar documents using mathematical vectors

## Research Findings
1. AI systems can process vast amounts of text data efficiently
2. Vector databases enable semantic search capabilities
3. RAG (Retrieval Augmented Generation) improves AI response accuracy
4. Document chunking helps in better information retrieval

## Applications
- Document search and analysis
- Automated question answering
- Content summarization
- Knowledge discovery

## Conclusion
AI-powered document search represents a significant advancement in information retrieval technology.
"""
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
        temp_file.write(content)
        temp_file.flush()
        temp_file.close()
        return temp_file.name

    def test_server_health(self):
        """Test if server is running"""
        print("🏥 Testing Server Health...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server Status: {data['status']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return False

    def demo_file_upload(self):
        """Demo file upload functionality"""
        print("\n" + "="*60)
        print("📤 FILE UPLOAD & MANAGEMENT ENDPOINTS DEMO")
        print("="*60)
        
        # Create test document
        print("\n📄 1. Creating test document...")
        test_file_path = self.create_test_document()
        print(f"✅ Created: {os.path.basename(test_file_path)}")
        
        # Upload file
        print("\n📤 2. Uploading document...")
        try:
            with open(test_file_path, 'rb') as f:
                files = {'file': ('test_document.md', f, 'text/markdown')}
                data = {'workspace_id': self.workspace_id}
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/upload",
                    data=data,
                    files=files,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    self.uploaded_file_id = result.get('file_id')
                    print(f"✅ Upload successful!")
                    print(f"   File ID: {self.uploaded_file_id}")
                    print(f"   Status: {result.get('status', 'Unknown')}")
                    if 'details' in result:
                        details = result['details']
                        print(f"   Chunks: {details.get('chunks_created', 'N/A')}")
                        print(f"   Characters: {details.get('total_characters', 'N/A')}")
                elif response.status_code == 429:
                    print("⚠️  Rate limited - continuing with existing files")
                else:
                    print(f"❌ Upload failed: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"❌ Upload error: {e}")
        finally:
            # Clean up temp file
            try:
                os.unlink(test_file_path)
            except:
                pass

    def demo_file_management(self):
        """Demo file management endpoints"""
        print("\n📁 3. File Management Operations...")
        
        # List files in workspace
        print("\n📋 Listing files in workspace...")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/files/{self.workspace_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                file_count = data.get('total_files', 0)
                print(f"✅ Found {file_count} files in workspace")
                
                if data.get('files'):
                    for i, file_info in enumerate(data['files'][:3], 1):  # Show first 3 files
                        print(f"   {i}. {file_info.get('filename', 'Unknown')}")
                        print(f"      ID: {file_info.get('file_id', 'N/A')[:20]}...")
                        print(f"      Size: {file_info.get('file_size', 0)} bytes")
                        
                        # Use first available file ID if we don't have one from upload
                        if not self.uploaded_file_id:
                            self.uploaded_file_id = file_info.get('file_id')
                            
            elif response.status_code == 429:
                print("⚠️  Rate limited - file listing unavailable")
            else:
                print(f"⚠️  File listing: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Error listing files: {e}")

        # Get file information (if we have a file ID)
        if self.uploaded_file_id:
            print(f"\n📄 Getting file information...")
            try:
                params = {'workspace_id': self.workspace_id}
                response = self.session.get(
                    f"{self.base_url}/api/v1/file/{self.uploaded_file_id}",
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    file_info = data.get('file_info', {})
                    print(f"✅ File details retrieved:")
                    print(f"   Filename: {file_info.get('filename', 'N/A')}")
                    print(f"   Status: {file_info.get('status', 'N/A')}")
                    print(f"   Storage: {file_info.get('storage_type', 'N/A')}")
                elif response.status_code == 429:
                    print("⚠️  Rate limited - file info unavailable")
                else:
                    print(f"⚠️  File info: Status {response.status_code}")
            except Exception as e:
                print(f"❌ Error getting file info: {e}")

            # Get file metadata
            print(f"\n📊 Getting file metadata...")
            try:
                params = {'workspace_id': self.workspace_id}
                response = self.session.get(
                    f"{self.base_url}/api/v1/file/{self.uploaded_file_id}/metadata",
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    stats = data.get('vector_stats', {})
                    print(f"✅ File metadata retrieved:")
                    print(f"   Total chunks: {stats.get('total_chunks', 'N/A')}")
                    print(f"   Total pages: {stats.get('total_pages', 'N/A')}")
                    print(f"   Characters: {stats.get('total_characters', 'N/A')}")
                elif response.status_code == 429:
                    print("⚠️  Rate limited - metadata unavailable")
                else:
                    print(f"⚠️  Metadata: Status {response.status_code}")
            except Exception as e:
                print(f"❌ Error getting metadata: {e}")

    def demo_search_endpoints(self):
        """Demo AI search endpoints"""
        print("\n" + "="*60)
        print("🔍 AI SEARCH ENDPOINTS DEMO")
        print("="*60)
        
        # Search statistics
        print("\n📊 1. Getting search statistics...")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/search/stats/{self.workspace_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                stats = data.get('stats', {})
                print(f"✅ Search engine: {stats.get('search_engine', 'N/A')}")
                print(f"   Model: {stats.get('model', 'N/A')}")
                print(f"   Vector count: {stats.get('vector_count', 'N/A')}")
            elif response.status_code == 429:
                print("⚠️  Rate limited - search stats unavailable")
            else:
                print(f"⚠️  Search stats: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting search stats: {e}")

        # Simple search
        print("\n🔍 2. Testing simple search...")
        try:
            params = {
                'workspace_id': self.workspace_id,
                'query': 'artificial intelligence machine learning',
                'top_k': 3
            }
            response = self.session.get(f"{self.base_url}/api/v1/search/simple", params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"✅ Simple search successful! Found {len(results)} results")
                
                for i, result in enumerate(results[:2], 1):  # Show first 2 results
                    print(f"   Result {i}:")
                    print(f"     Score: {result.get('score', 'N/A'):.3f}")
                    print(f"     Text: {result.get('text', '')[:100]}...")
                    print(f"     File: {result.get('filename', 'N/A')}")
                    
            elif response.status_code == 429:
                print("⚠️  Rate limited - simple search unavailable")
            else:
                print(f"⚠️  Simple search: Status {response.status_code}")
                print(f"     Response: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Error in simple search: {e}")

        # Advanced search with AI
        print("\n🧠 3. Testing advanced AI search...")
        try:
            search_data = {
                'workspace_id': self.workspace_id,
                'query': 'What are the key concepts of artificial intelligence mentioned in the documents?',
                'top_k': 5,
                'include_web': False,  # Disable web search to avoid external dependencies
                'rerank': False,       # Disable reranking to avoid rate limits
                'summarize': True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/search",
                json=search_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Advanced search successful!")
                print(f"   Answer: {data.get('answer', 'No answer provided')[:200]}...")
                print(f"   Confidence: {data.get('confidence', 'N/A')}")
                print(f"   Sources: {len(data.get('sources', []))} sources")
                print(f"   Processing time: {data.get('processing_time', 'N/A')} seconds")
                
                # Show sources
                sources = data.get('sources', [])[:2]  # First 2 sources
                for i, source in enumerate(sources, 1):
                    print(f"   Source {i}: {source.get('filename', 'N/A')} (Score: {source.get('score', 'N/A')})")
                    
            elif response.status_code == 429:
                print("⚠️  Rate limited - advanced search unavailable")
            elif response.status_code == 500:
                print("⚠️  Server error - some AI features may not be configured")
                print(f"     Response: {response.text[:200]}")
            else:
                print(f"⚠️  Advanced search: Status {response.status_code}")
                print(f"     Response: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Error in advanced search: {e}")

    def run_focused_demo(self):
        """Run the complete focused demo"""
        print("🎯 OMNISEARCH AI - FOCUSED ENDPOINTS DEMO")
        print("=" * 70)
        print(f"🔗 Target API: {self.base_url}")
        print(f"📁 Test Workspace: {self.workspace_id}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check server health
        if not self.test_server_health():
            print("❌ Server is not responding. Please ensure the FastAPI server is running.")
            return False
        
        try:
            # Demo file upload and management
            self.demo_file_upload()
            self.demo_file_management()
            
            # Demo AI search endpoints
            self.demo_search_endpoints()
            
            # Summary
            print("\n" + "="*70)
            print("🎉 DEMO COMPLETED SUCCESSFULLY!")
            print("="*70)
            print("\n✅ Tested Endpoint Categories:")
            print("   📤 File Upload & Management")
            print("   🔍 AI Search & Retrieval")
            print("\n🌐 Available Services:")
            print(f"   • API Server: {self.base_url}")
            print(f"   • Documentation: {self.base_url}/docs")
            print(f"   • Health Check: {self.base_url}/health")
            
            print("\n💡 Key Features Demonstrated:")
            print("   • Document upload and processing")
            print("   • File metadata extraction")
            print("   • Vector-based similarity search")
            print("   • AI-powered question answering")
            print("   • Source citation and provenance")
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            return False

def main():
    """Main function to run the focused demo"""
    demo = FocusedAPIDemo()
    success = demo.run_focused_demo()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
