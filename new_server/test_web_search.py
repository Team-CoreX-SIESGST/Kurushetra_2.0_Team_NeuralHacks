#!/usr/bin/env python3
"""
Test script for the web search functionality
"""

import asyncio
import json
from web_search import WebSearchEngine
from rag_system import RAGSystem

async def test_web_search():
    """Test the web search functionality"""
    print("🔍 Testing Web Search Functionality")
    print("=" * 50)
    
    # Initialize the web search engine
    search_engine = WebSearchEngine()
    
    # Test content
    test_content = """
    Artificial intelligence (AI) and machine learning (ML) are revolutionizing 
    various industries. Deep learning algorithms, neural networks, and natural 
    language processing are key technologies in this field. Companies are using 
    AI for data analysis, computer vision, and automated decision making.
    """
    
    test_extracted_data = {
        "content_type": "text",
        "content": test_content
    }
    
    print("📝 Test content:")
    print(test_content.strip())
    print("\n" + "=" * 50)
    
    try:
        # Test web search
        print("🌐 Searching for related web URLs...")
        results = await search_engine.find_relevant_urls(test_content, test_extracted_data, max_urls=5)
        
        print("✅ Web search results:")
        print(f"📊 Found {len(results.get('related_urls', []))} relevant URLs")
        
        if results.get('related_urls'):
            print("\n📄 Related URLs:")
            for i, url in enumerate(results['related_urls'][:3], 1):
                print(f"{i}. {url['title']}")
                print(f"   🔗 {url['url']}")
                print(f"   📖 {url['description'][:100]}...")
                print(f"   🏷️  Source: {url['source']}")
                print()
        
        if results.get('search_metadata'):
            metadata = results['search_metadata']
            print(f"🔑 Keywords extracted: {metadata.get('keywords_extracted', [])[:5]}")
            print(f"🔍 Search queries used: {metadata.get('queries_used', [])}")
        
        print("\n" + "=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Error in web search test: {str(e)}")
        return False

async def test_rag_with_urls():
    """Test the RAG system with URL integration"""
    print("🤖 Testing RAG System with Web URLs")
    print("=" * 50)
    
    # Initialize RAG system
    rag_system = RAGSystem()
    
    # Check if API is configured
    if rag_system.check_api_status() != "configured":
        print("⚠️  Gemini API not configured, skipping RAG test")
        return False
    
    # Test data
    test_extracted_data = {
        "content_type": "text",
        "content": "Python programming language data science libraries pandas numpy matplotlib",
        "file_metadata": {
            "original_filename": "test_document.txt"
        }
    }
    
    try:
        print("📝 Generating summary with related URLs...")
        summary_with_urls = await rag_system.generate_summary_with_urls(test_extracted_data, include_urls=True)
        
        if "error" in summary_with_urls:
            print(f"❌ Error in summary generation: {summary_with_urls['error']}")
            return False
        
        print("✅ Summary generated successfully!")
        
        if summary_with_urls.get('related_web_resources'):
            web_resources = summary_with_urls['related_web_resources']
            urls_found = len(web_resources.get('related_urls', []))
            print(f"🌐 Found {urls_found} related web resources")
            
            if urls_found > 0:
                print("\n📄 Sample URLs:")
                for url in web_resources['related_urls'][:2]:
                    print(f"• {url['title']}")
                    print(f"  🔗 {url['url']}")
        else:
            print("⚠️  No web resources found or web search failed")
        
        print("\n" + "=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Error in RAG test: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Web URL Functionality Tests\n")
    
    # Test 1: Web search functionality
    web_search_success = await test_web_search()
    
    # Test 2: RAG system with URLs
    rag_success = await test_rag_with_urls()
    
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    print(f"Web Search Test: {'✅ PASSED' if web_search_success else '❌ FAILED'}")
    print(f"RAG with URLs Test: {'✅ PASSED' if rag_success else '❌ FAILED'}")
    
    if web_search_success and rag_success:
        print("\n🎉 All tests passed! Web URL functionality is working correctly.")
    elif web_search_success:
        print("\n⚠️  Web search is working, but RAG integration may have issues.")
        print("   Check your Gemini API key configuration.")
    else:
        print("\n❌ Tests failed. Check the implementation and error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
