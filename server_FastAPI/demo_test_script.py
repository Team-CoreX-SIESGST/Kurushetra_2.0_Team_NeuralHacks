#!/usr/bin/env python3
"""
OmniSearch AI Demo Test Script
Tests all endpoints and functionality with demo data
"""

import asyncio
import aiohttp
import json
import os
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
WORKSPACE_ID = "demo-workspace"

class OmniSearchDemo:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """Test health check endpoint"""
        print("🏥 Testing health check...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                data = await response.json()
                print(f"✅ Health check: {data['status']}")
                return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    async def test_root_endpoint(self):
        """Test root endpoint"""
        print("🏠 Testing root endpoint...")
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                data = await response.json()
                print(f"✅ Root endpoint: {data['message']}")
                return True
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
            return False
    
    async def test_file_upload(self, file_path):
        """Test file upload endpoint"""
        print(f"📤 Testing file upload: {file_path}")
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as file:
                data = aiohttp.FormData()
                data.add_field('workspace_id', WORKSPACE_ID)
                data.add_field('file', file, filename=os.path.basename(file_path))
                
                async with self.session.post(f"{self.base_url}/api/v1/upload", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ File uploaded: {result.get('file_id', 'Unknown ID')}")
                        return result.get('file_id')
                    else:
                        print(f"❌ Upload failed: {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return None
    
    async def test_file_list(self):
        """Test file listing endpoint"""
        print(f"📂 Testing file list for workspace: {WORKSPACE_ID}")
        try:
            async with self.session.get(f"{self.base_url}/api/v1/files?workspace_id={WORKSPACE_ID}") as response:
                if response.status == 200:
                    files = await response.json()
                    print(f"✅ Found {len(files)} files in workspace")
                    return files
                else:
                    print(f"❌ File list failed: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ File list error: {e}")
            return []
    
    async def test_simple_search(self, query):
        """Test simple search endpoint"""
        print(f"🔍 Testing simple search: '{query}'")
        try:
            params = {
                'workspace_id': WORKSPACE_ID,
                'query': query,
                'top_k': 5
            }
            async with self.session.get(f"{self.base_url}/api/v1/search/simple", params=params) as response:
                if response.status == 200:
                    results = await response.json()
                    print(f"✅ Simple search found {len(results.get('results', []))} results")
                    return results
                else:
                    print(f"❌ Simple search failed: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Simple search error: {e}")
            return None
    
    async def test_full_search(self, query):
        """Test full AI search pipeline"""
        print(f"🤖 Testing full AI search: '{query}'")
        try:
            payload = {
                "workspace_id": WORKSPACE_ID,
                "query": query,
                "top_k": 5,
                "include_web": False,  # Disable web search for demo
                "rerank": True,
                "summarize": True
            }
            
            async with self.session.post(f"{self.base_url}/api/v1/search", json=payload) as response:
                if response.status == 200:
                    results = await response.json()
                    print(f"✅ Full search completed:")
                    print(f"   Answer: {results.get('answer', 'No answer')[:100]}...")
                    print(f"   Confidence: {results.get('confidence', 0)}")
                    print(f"   Sources: {len(results.get('sources', []))}")
                    return results
                else:
                    text = await response.text()
                    print(f"❌ Full search failed: {response.status}")
                    print(f"   Response: {text[:200]}...")
                    return None
        except Exception as e:
            print(f"❌ Full search error: {e}")
            return None
    
    async def test_file_details(self, file_id):
        """Test file details endpoint"""
        print(f"📄 Testing file details: {file_id}")
        try:
            async with self.session.get(f"{self.base_url}/api/v1/file/{file_id}") as response:
                if response.status == 200:
                    details = await response.json()
                    print(f"✅ File details retrieved: {details.get('filename', 'Unknown')}")
                    return details
                else:
                    print(f"❌ File details failed: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ File details error: {e}")
            return None
    
    async def test_search_stats(self):
        """Test search statistics endpoint"""
        print(f"📊 Testing search stats for workspace: {WORKSPACE_ID}")
        try:
            async with self.session.get(f"{self.base_url}/api/v1/search/stats/{WORKSPACE_ID}") as response:
                if response.status == 200:
                    stats = await response.json()
                    print(f"✅ Search stats retrieved")
                    return stats
                else:
                    print(f"❌ Search stats failed: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Search stats error: {e}")
            return None

async def run_demo():
    """Run comprehensive demo test"""
    print("🚀 Starting OmniSearch AI Demo Tests")
    print("=" * 50)
    
    async with OmniSearchDemo() as demo:
        # Basic connectivity tests
        await demo.test_health_check()
        await demo.test_root_endpoint()
        
        print("\n" + "=" * 50)
        print("📁 File Management Tests")
        print("=" * 50)
        
        # Test file upload
        demo_files = [
            "demo-workspace/ai_research_sample.txt",
            "demo-workspace/machine_learning_fundamentals.txt", 
            "demo-workspace/deep_learning_guide.txt"
        ]
        
        uploaded_files = []
        for file_path in demo_files:
            if os.path.exists(file_path):
                file_id = await demo.test_file_upload(file_path)
                if file_id:
                    uploaded_files.append(file_id)
            else:
                print(f"⚠️  Demo file not found: {file_path}")
        
        # Test file listing
        files = await demo.test_file_list()
        
        # Test file details for uploaded files
        if uploaded_files:
            await demo.test_file_details(uploaded_files[0])
        
        print("\n" + "=" * 50)
        print("🔍 Search Tests")
        print("=" * 50)
        
        # Test search queries
        test_queries = [
            "key findings of AI",
            "what is machine learning",
            "deep learning architectures",
            "neural networks fundamentals",
            "best practices for ML"
        ]
        
        for query in test_queries:
            print(f"\n🔎 Testing query: '{query}'")
            
            # Simple search
            simple_results = await demo.test_simple_search(query)
            
            # Full search with small delay
            await asyncio.sleep(2)
            full_results = await demo.test_full_search(query)
            
            print("-" * 30)
        
        print("\n" + "=" * 50)
        print("📊 Statistics Tests")
        print("=" * 50)
        
        # Test search statistics
        await demo.test_search_stats()
        
        print("\n" + "=" * 50)
        print("✅ Demo Tests Completed!")
        print("=" * 50)

def create_demo_files():
    """Ensure demo files exist"""
    demo_dir = Path("demo-workspace")
    demo_dir.mkdir(exist_ok=True)
    
    # Files are already created by previous function calls
    demo_files = [
        "ai_research_sample.txt",
        "machine_learning_fundamentals.txt",
        "deep_learning_guide.txt"
    ]
    
    existing_files = []
    for filename in demo_files:
        file_path = demo_dir / filename
        if file_path.exists():
            existing_files.append(str(file_path))
    
    print(f"📁 Found {len(existing_files)} demo files ready for testing")
    return existing_files

if __name__ == "__main__":
    print("🔧 Preparing demo environment...")
    create_demo_files()
    
    print("\n🌐 Starting server connectivity test...")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    input("Press Enter to continue when server is ready...")
    
    # Run the demo
    asyncio.run(run_demo())
