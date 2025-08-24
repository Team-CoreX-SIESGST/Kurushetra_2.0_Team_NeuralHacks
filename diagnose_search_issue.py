#!/usr/bin/env python3
"""
Diagnostic script to identify search issues in OmniSearch AI.
Helps troubleshoot the JSON parsing error in intelligent search.
"""

import requests
import json
import time
import asyncio
import aiohttp

async def test_ollama_connection():
    """Test direct connection to Ollama service."""
    print("🔍 Testing Ollama Connection")
    print("=" * 30)
    
    ollama_host = "http://localhost:11434"
    
    try:
        # Test basic connectivity
        print("1. Testing Ollama API connectivity...")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ollama_host}/api/tags") as response:
                if response.status == 200:
                    result = await response.json()
                    models = result.get('models', [])
                    print(f"✅ Ollama connected - {len(models)} models available")
                    for model in models[:3]:  # Show first 3 models
                        print(f"   - {model.get('name', 'unnamed')}")
                else:
                    print(f"❌ Ollama API returned {response.status}")
                    return False
        
        # Test model generation
        print("\n2. Testing model generation...")
        
        test_payload = {
            "model": "llama2:7b-chat",
            "prompt": "Reply with just: research_longform",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 10
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{ollama_host}/api/generate", json=test_payload) as response:
                if response.status == 200:
                    result = await response.json()
                    model_response = result.get("response", "")
                    print(f"✅ Model generation works")
                    print(f"   Response: '{model_response.strip()}'")
                    print(f"   Response length: {len(model_response)}")
                    
                    if model_response.strip() == "":
                        print("⚠️  WARNING: Empty response from model")
                        return False
                else:
                    print(f"❌ Model generation failed: {response.status}")
                    response_text = await response.text()
                    print(f"   Error: {response_text}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

def test_backend_services():
    """Test backend services availability."""
    print("\n🔍 Testing Backend Services")
    print("=" * 30)
    
    try:
        # Test API health
        print("1. Testing API health...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is healthy")
        else:
            print(f"❌ Backend API health check failed: {response.status_code}")
            return False
        
        # Test MongoDB
        print("\n2. Testing MongoDB connection...")
        try:
            import pymongo
            client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
            client.server_info()
            print("✅ MongoDB connection successful")
        except Exception as mongo_error:
            print(f"⚠️  MongoDB connection failed: {mongo_error}")
            print("   (This may not affect basic search functionality)")
        
        # Test Redis (optional)
        print("\n3. Testing Redis connection...")
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=3)
            r.ping()
            print("✅ Redis connection successful")
        except Exception as redis_error:
            print(f"⚠️  Redis connection failed: {redis_error}")
            print("   (Redis is optional for basic functionality)")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend services test failed: {e}")
        return False

def test_search_with_detailed_logging():
    """Test search with detailed error logging."""
    print("\n🔍 Testing Search with Detailed Logging")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test minimal search (no AI)
        print("1. Testing minimal search (no AI processing)...")
        
        minimal_payload = {
            "workspace_id": "diagnostic-test",
            "query": "test query",
            "top_k": 5,
            "include_web": False,
            "rerank": False,
            "summarize": False
        }
        
        response = requests.post(f"{base_url}/api/v1/search", json=minimal_payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Minimal search successful")
            print(f"   Answer: {result.get('answer', 'No answer')}")
            print(f"   Search type: {result.get('metadata', {}).get('search_type', 'unknown')}")
        else:
            print(f"❌ Minimal search failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test search with AI (this is where the error likely occurs)
        print("\n2. Testing search with AI processing...")
        
        ai_payload = {
            "workspace_id": "diagnostic-test",
            "query": "test query for AI processing",
            "top_k": 5,
            "include_web": False,
            "rerank": False,
            "summarize": True  # This triggers the JSON parsing
        }
        
        response = requests.post(f"{base_url}/api/v1/search", json=ai_payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI search successful")
            print(f"   Answer: {result.get('answer', 'No answer')}")
            print(f"   Confidence: {result.get('confidence', 0)}")
            print(f"   Search type: {result.get('metadata', {}).get('search_type', 'unknown')}")
        elif response.status_code == 500:
            result = response.json()
            print("⚠️  AI search returned error (this is where JSON parsing likely fails)")
            print(f"   Answer: {result.get('answer', 'No answer')}")
            error_info = result.get('metadata', {}).get('error', 'No error details')
            print(f"   Error details: {error_info}")
            
            if "Expecting value: line 1 column 1 (char 0)" in error_info:
                print("🎯 IDENTIFIED: This is the JSON parsing error!")
                print("   Cause: Ollama is returning empty response")
        else:
            print(f"❌ AI search failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

async def main():
    """Run all diagnostic tests."""
    print("🩺 OmniSearch AI - Search Diagnostic Tool")
    print("=" * 50)
    
    print("This tool will help identify the source of the JSON parsing error")
    print("in the intelligent search feature.\n")
    
    # Run diagnostics
    results = []
    
    # Test Ollama
    results.append(await test_ollama_connection())
    
    # Test backend services  
    results.append(test_backend_services())
    
    # Test search functionality
    results.append(test_search_with_detailed_logging())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Diagnostic Results")
    print("=" * 25)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All systems operational!")
        print("\nIf you're still experiencing the JSON parsing error:")
        print("1. Check the server console logs for detailed error messages")
        print("2. Ensure Ollama models are fully downloaded and working")  
        print("3. Try restarting the Ollama service")
    else:
        print("❌ Issues detected!")
        print("\nCommon fixes:")
        if results[0] == False:
            print("- Start Ollama: ollama serve")
            print("- Install models: ollama pull llama2:7b-chat")
        if results[1] == False:
            print("- Start FastAPI server: python -m uvicorn app.main:app --reload --port 8000")
        print("- Check the improved error handling should prevent crashes now")

if __name__ == "__main__":
    asyncio.run(main())
