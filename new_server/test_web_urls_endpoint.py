#!/usr/bin/env python3
"""
Test script for the new /fetch-web-urls endpoint
This demonstrates how to use the dedicated web URLs fetching endpoint
"""

import requests
import json

# API base URL
API_BASE_URL = "http://localhost:8000"

def test_fetch_web_urls_with_content():
    """Test the endpoint with simple text content"""
    print("🧪 Testing /fetch-web-urls with content text...")
    
    # Test data - simple text about AI/ML
    test_data = {
        "content": "Natural Language Processing and Machine Learning using transformer models like BERT and GPT for text analysis and generation.",
        "max_urls": 8,
        "ai_categories": {
            "primary_domains": ["artificial_intelligence", "machine_learning", "natural_language_processing"],
            "topics": ["transformers", "BERT", "GPT", "text analysis", "language models"],
            "search_terms": ["NLP", "transformers", "BERT", "machine learning"],
            "academic_fields": ["computer science", "artificial intelligence"],
            "tools_technologies": ["BERT", "GPT", "transformers", "PyTorch", "TensorFlow"]
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/fetch-web-urls", json=test_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Found {len(result['urls'])} URLs")
            
            # Pretty print the results
            print("\n📋 Response:")
            print(json.dumps(result, indent=2))
            
            # Show just the URLs array
            print(f"\n🌐 URLs Array ({len(result['urls'])} items):")
            for i, url in enumerate(result['urls'], 1):
                print(f"{i}. {url['title']}")
                print(f"   URL: {url['url']}")
                print(f"   Source: {url['source']}")
                print()
                
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_fetch_web_urls_with_extracted_data():
    """Test the endpoint with structured extracted data"""
    print("\n🧪 Testing /fetch-web-urls with extracted_data...")
    
    # Test data - structured data format
    test_data = {
        "extracted_data": {
            "content_type": "text",
            "content": "Deep learning research on computer vision and image recognition using convolutional neural networks and transfer learning techniques.",
            "total_words": 20,
            "total_characters": 125
        },
        "max_urls": 5
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/fetch-web-urls", json=test_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Found {len(result['urls'])} URLs")
            
            # Show metadata
            metadata = result['search_metadata']
            print(f"\n📊 Search Metadata:")
            print(f"   Total URLs: {metadata['total_urls_found']}")
            print(f"   Content Type: {metadata['content_type']}")
            print(f"   AI Categories Used: {metadata['ai_categories_used']}")
            print(f"   Search Time: {metadata['search_timestamp']}")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_invalid_request():
    """Test error handling with invalid request"""
    print("\n🧪 Testing error handling...")
    
    # Empty request - should fail
    test_data = {}
    
    try:
        response = requests.post(f"{API_BASE_URL}/fetch-web-urls", json=test_data)
        
        if response.status_code == 400:
            print("✅ Error handling works correctly")
            print(f"Error message: {response.json()['detail']}")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Web URLs Fetch Endpoint")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            exit(1)
    except:
        print("❌ Server is not accessible. Make sure it's running on localhost:8000")
        exit(1)
    
    # Run tests
    test_fetch_web_urls_with_content()
    test_fetch_web_urls_with_extracted_data() 
    test_invalid_request()
    
    print("\n🎉 Testing completed!")
