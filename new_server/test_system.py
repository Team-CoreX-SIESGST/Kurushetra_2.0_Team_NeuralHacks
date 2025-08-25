#!/usr/bin/env python3
"""
Test script for File Processing & RAG System
"""

import os
import json
import tempfile
import asyncio
import aiohttp
from pathlib import Path

# Test data for creating sample files
SAMPLE_TEXT = """
This is a sample document for testing the file processing system.
It contains multiple paragraphs and should be processed correctly.

Key points:
1. System should extract text content
2. Convert to JSON format
3. Generate AI-powered summaries
4. Handle various file formats

Technical specifications:
- Supports PDF, Word, Excel, PowerPoint, CSV, and more
- Uses FastAPI for web services
- Integrates with Gemini API for AI summaries
- Provides comprehensive error handling
"""

SAMPLE_JSON = {
    "title": "Test Document",
    "content": SAMPLE_TEXT,
    "metadata": {
        "author": "Test System",
        "created": "2024-01-15",
        "type": "test_document"
    },
    "data": [
        {"name": "Item 1", "value": 100, "category": "A"},
        {"name": "Item 2", "value": 200, "category": "B"},
        {"name": "Item 3", "value": 300, "category": "A"}
    ]
}

SAMPLE_CSV_DATA = """Name,Age,City,Score
John Doe,30,New York,85
Jane Smith,25,Los Angeles,92
Bob Johnson,35,Chicago,78
Alice Brown,28,Houston,88
"""

def create_test_files():
    """Create sample test files"""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create text file
    with open(test_dir / "sample.txt", "w", encoding="utf-8") as f:
        f.write(SAMPLE_TEXT)
    
    # Create JSON file
    with open(test_dir / "sample.json", "w", encoding="utf-8") as f:
        json.dump(SAMPLE_JSON, f, indent=2)
    
    # Create CSV file
    with open(test_dir / "sample.csv", "w", encoding="utf-8") as f:
        f.write(SAMPLE_CSV_DATA)
    
    # Create HTML file
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Document</title>
    </head>
    <body>
        <h1>Test Document</h1>
        <p>{SAMPLE_TEXT}</p>
    </body>
    </html>
    """
    with open(test_dir / "sample.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Create Markdown file
    md_content = f"""
    # Test Document
    
    {SAMPLE_TEXT}
    
    ## Technical Details
    
    This is a **markdown** file for testing purposes.
    """
    with open(test_dir / "sample.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print("✅ Test files created in test_files/ directory")
    return test_dir

def test_file_processor():
    """Test the file processor module"""
    print("🔧 Testing FileProcessor...")
    
    try:
        from file_processor import FileProcessor
        
        processor = FileProcessor()
        
        # Test supported formats
        formats = processor.get_supported_formats()
        print(f"✅ Supported formats: {len(formats)} formats")
        
        # Test format validation
        assert processor.is_supported_format("test.txt")
        assert processor.is_supported_format("test.json")
        assert not processor.is_supported_format("test.unsupported")
        print("✅ Format validation works")
        
        # Test text file processing
        test_dir = create_test_files()
        text_file = test_dir / "sample.txt"
        
        if text_file.exists():
            result = processor.process_file(str(text_file), "sample.txt")
            assert result["content_type"] == "text"
            assert "content" in result
            print("✅ Text file processing works")
        
        # Test JSON file processing
        json_file = test_dir / "sample.json"
        if json_file.exists():
            result = processor.process_file(str(json_file), "sample.json")
            assert result["content_type"] == "json"
            assert "data" in result
            print("✅ JSON file processing works")
        
        print("✅ FileProcessor tests passed")
        return True
        
    except Exception as e:
        print(f"❌ FileProcessor test failed: {e}")
        return False

def test_rag_system():
    """Test the RAG system"""
    print("🤖 Testing RAG System...")
    
    try:
        from rag_system import RAGSystem
        
        rag = RAGSystem()
        
        # Test API status check
        status = rag.check_api_status()
        print(f"✅ API status: {status}")
        
        # Test timestamp generation
        timestamp = rag.get_current_timestamp()
        print(f"✅ Timestamp generation: {timestamp}")
        
        # Test fallback summary
        sample_data = {
            "content_type": "text",
            "content": SAMPLE_TEXT,
            "total_words": 100,
            "total_characters": 500
        }
        
        fallback = rag._generate_fallback_summary(sample_data)
        assert fallback["type"] == "fallback_summary"
        print("✅ Fallback summary generation works")
        
        # Test context preparation
        context = rag._prepare_context(sample_data)
        assert len(context) > 0
        print("✅ Context preparation works")
        
        print("✅ RAG System tests passed")
        return True
        
    except Exception as e:
        print(f"❌ RAG System test failed: {e}")
        return False

async def test_api_endpoints():
    """Test the API endpoints"""
    print("🌐 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Health endpoint works")
                else:
                    print("⚠️ Health endpoint returned status:", response.status)
            
            # Test supported formats endpoint
            async with session.get(f"{base_url}/supported-formats") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Supported formats endpoint: {len(result.get('supported_formats', []))} formats")
                else:
                    print("⚠️ Supported formats endpoint returned status:", response.status)
            
            # Test file processing endpoint
            test_dir = Path("test_files")
            if (test_dir / "sample.txt").exists():
                data = aiohttp.FormData()
                data.add_field('file',
                             open(test_dir / "sample.txt", 'rb'),
                             filename='sample.txt',
                             content_type='text/plain')
                
                async with session.post(f"{base_url}/process-file", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ File processing endpoint works")
                    else:
                        print("⚠️ File processing endpoint returned status:", response.status)
            
            # Test JSON summarization endpoint
            sample_json = {"test": "data", "content": SAMPLE_TEXT}
            async with session.post(f"{base_url}/summarize-json", json=sample_json) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ JSON summarization endpoint works")
                else:
                    print("⚠️ JSON summarization endpoint returned status:", response.status)
        
        return True
        
    except aiohttp.ClientError as e:
        print(f"❌ API test failed - Server not running? {e}")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("📦 Testing imports...")
    
    modules_to_test = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("aiohttp", "HTTP client"),
        ("pandas", "Data processing"),
        ("json", "JSON handling"),
        ("pathlib", "Path handling"),
        ("tempfile", "Temporary files"),
        ("datetime", "Date/time handling")
    ]
    
    optional_modules = [
        ("PyPDF2", "PDF processing"),
        ("pdfplumber", "Advanced PDF processing"),
        ("docx", "Word document processing"),
        ("openpyxl", "Excel processing"),
        ("pptx", "PowerPoint processing"),
        ("PIL", "Image processing"),
        ("pytesseract", "OCR"),
        ("bs4", "HTML parsing"),
        ("markdown", "Markdown processing")
    ]
    
    success_count = 0
    
    # Test required modules
    for module, description in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
            success_count += 1
        except ImportError:
            print(f"❌ {module} - {description} (REQUIRED)")
    
    # Test optional modules
    optional_success = 0
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
            optional_success += 1
        except ImportError:
            print(f"⚠️  {module} - {description} (optional)")
    
    print(f"\n📊 Import Results:")
    print(f"   Required modules: {success_count}/{len(modules_to_test)}")
    print(f"   Optional modules: {optional_success}/{len(optional_modules)}")
    
    return success_count == len(modules_to_test)

def generate_test_report(results):
    """Generate a test report"""
    print("\n" + "="*60)
    print("📋 TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name:<25} {status}")
    
    print(f"\n📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! System is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed_tests == total_tests

async def main():
    """Main test function"""
    print("🚀 File Processing & RAG System - Test Suite")
    print("="*60)
    
    results = {}
    
    # Run tests
    results["Imports"] = test_imports()
    results["FileProcessor"] = test_file_processor()
    results["RAG System"] = test_rag_system()
    
    # API tests require the server to be running
    print("\nℹ️  For API tests, make sure the server is running:")
    print("   python main.py")
    
    try_api = input("\nTest API endpoints? (y/n): ").lower().strip()
    if try_api == 'y':
        results["API Endpoints"] = await test_api_endpoints()
    else:
        print("⏭️  Skipping API tests")
    
    # Generate report
    all_passed = generate_test_report(results)
    
    # Cleanup
    test_dir = Path("test_files")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print("\n🧹 Cleaned up test files")
    
    return all_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        exit(1)
