#!/usr/bin/env python3
"""
Quick Demo Script for OmniSearch AI
Tests core functionality without external dependencies
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def demo_core_functionality():
    """Demo core AI functionality without server"""
    print("🚀 OmniSearch AI Core Functionality Demo")
    print("=" * 60)
    
    try:
        # Test 1: Settings and Configuration
        print("\n📋 1. Testing Configuration...")
        from app.settings import settings
        print(f"✅ Demo mode: {settings.demo_mode}")
        print(f"✅ Server port: {settings.server_port}")
        print(f"✅ Vector DB type: {settings.vector_db_type}")
        
        # Test 2: Model Router
        print("\n🧠 2. Testing AI Model Router...")
        from app.services.model_router import ModelRouter
        router = ModelRouter()
        
        test_queries = [
            "key findings of AI research",
            "what is machine learning",
            "write a Python function",
            "summarize this document"
        ]
        
        for query in test_queries:
            intent = await router.classify_intent(query)
            print(f"   Query: '{query[:30]}...' → Intent: {intent}")
        
        # Test 3: Embeddings Service
        print("\n🔤 3. Testing Embeddings Service...")
        from app.services.embeddings import EmbeddingsService
        embeddings_service = EmbeddingsService()
        await embeddings_service.initialize()
        
        test_text = "Artificial intelligence is transforming the world."
        embedding = embeddings_service.generate_single_embedding(test_text)
        print(f"✅ Generated embedding vector of dimension: {len(embedding)}")
        
        # Test 4: Vector Database
        print("\n🗃️  4. Testing Vector Database...")
        from app.services.vectordb import VectorDBService
        vector_db = VectorDBService("demo-workspace")
        await vector_db.initialize(embeddings_service.get_embedding_dimension())
        
        # Add some sample data
        sample_docs = [
            {"id": "doc1", "text": "Machine learning is a subset of artificial intelligence.", "metadata": {"source": "demo"}},
            {"id": "doc2", "text": "Deep learning uses neural networks with multiple layers.", "metadata": {"source": "demo"}},
            {"id": "doc3", "text": "Natural language processing helps computers understand text.", "metadata": {"source": "demo"}}
        ]
        
        # Generate embeddings and add to vector DB
        embeddings_batch = []
        for doc in sample_docs:
            embedding = embeddings_service.generate_single_embedding(doc["text"])
            embeddings_batch.append(embedding)
        
        # Convert to numpy array and add all at once
        import numpy as np
        embeddings_array = np.array(embeddings_batch).astype('float32')
        vector_db.add_vectors(embeddings_array, sample_docs)
        
        print(f"✅ Added {len(sample_docs)} sample documents to vector database")
        
        # Test search
        query_embedding = embeddings_service.generate_single_embedding("What is machine learning?")
        query_embedding = np.array(query_embedding).astype('float32')
        results = vector_db.search(query_embedding, top_k=2)
        print(f"✅ Search found {len(results)} relevant documents")
        
        # Test 5: File Processing (if demo files exist)
        print("\n📁 5. Testing File Processing...")
        demo_files = list(Path("demo-workspace").glob("*.txt"))
        if demo_files:
            print(f"✅ Found {len(demo_files)} demo files:")
            for file in demo_files[:3]:  # Show first 3
                print(f"   - {file.name}")
                
            # Test file ingestion
            from app.services.ingest import IngestService
            ingest_service = IngestService()
            
            if demo_files:
                sample_file = demo_files[0]
                print(f"   Processing sample file: {sample_file.name}")
                
                # Read and process file
                with open(sample_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                chunks = ingest_service._create_chunks(content)
                print(f"   ✅ Split into {len(chunks)} chunks")
                
        else:
            print("⚠️  No demo files found in demo-workspace/")
        
        # Test 6: Authentication (Demo Mode)
        print("\n🔐 6. Testing Authentication (Demo Mode)...")
        from app.middlewares.auth import get_demo_user
        demo_user = get_demo_user()
        print(f"✅ Demo user: {demo_user['name']} (ID: {demo_user['user_id']})")
        
        # Test 7: API Response Utilities
        print("\n📤 7. Testing API Utilities...")
        from app.utils.api_response import create_success_response, create_error_response
        
        success_resp = create_success_response("Test successful", {"test": "data"})
        error_resp = create_error_response("Test error", 400)
        print("✅ API response utilities working")
        
        print("\n" + "=" * 60)
        print("🎉 Core Functionality Demo Completed Successfully!")
        print("=" * 60)
        
        print("\n🌐 Next Steps:")
        print("1. Start the server: python -m uvicorn app.main:app --reload --port 8000")
        print("2. Visit: http://localhost:8000/docs for API documentation")
        print("3. Run full demo: python demo_test_script.py (with server running)")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

def check_demo_data():
    """Check and display demo data status"""
    print("\n📊 Demo Data Status:")
    print("-" * 30)
    
    demo_dir = Path("demo-workspace")
    if demo_dir.exists():
        files = list(demo_dir.glob("*"))
        print(f"✅ Demo workspace exists with {len(files)} files")
        
        txt_files = list(demo_dir.glob("*.txt"))
        pdf_files = list(demo_dir.glob("*.pdf"))
        
        if txt_files:
            print(f"   📄 Text files: {len(txt_files)}")
            for f in txt_files[:3]:
                size = f.stat().st_size
                print(f"      - {f.name} ({size:,} bytes)")
        
        if pdf_files:
            print(f"   📄 PDF files: {len(pdf_files)}")
            
    else:
        print("❌ Demo workspace not found")
    
    # Check vector database
    vector_dirs = [d for d in Path(".").iterdir() if d.is_dir() and "vector" in d.name.lower()]
    if vector_dirs:
        print(f"✅ Found {len(vector_dirs)} vector database directories")

if __name__ == "__main__":
    print("🎯 OmniSearch AI - Quick Demo")
    check_demo_data()
    asyncio.run(demo_core_functionality())
