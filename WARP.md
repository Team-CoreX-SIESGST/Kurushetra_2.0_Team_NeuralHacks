# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

OmniSearch AI is an AI-powered document search and analysis system that combines intelligent document ingestion, vector search, web enrichment, and AI-powered summarization. The system features a FastAPI backend with a Streamlit frontend and includes intelligent model routing based on query intent.

## Architecture

The system follows a modular service-oriented architecture with three main components:

1. **FastAPI Backend** (`server_FastAPI/`) - Core AI services and API endpoints
2. **Streamlit Frontend** (`streamlit_frontend/`) - Web-based user interface  
3. **Next.js Client** (`client/`) - Alternative React frontend (legacy)

### Key AI Pipeline Components

- **Model Router** - Routes queries to appropriate models based on intent classification
- **Embeddings Service** - Text vectorization using sentence-transformers
- **Vector Database** - FAISS-based similarity search
- **Reranker** - Cross-encoder models for result relevance
- **Summarizer** - LLM-powered answer generation with source citations
- **Web Search** - External content enrichment

## Common Development Commands

### Full Stack Development

```bash
# Quick start - run everything
python demo_full_stack.py --demo

# Start backend only
python demo_full_stack.py --backend-only

# Start frontend only  
python demo_full_stack.py --frontend-only
```

### Backend Development (server_FastAPI/)

```bash
cd server_FastAPI

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp example_env.txt .env

# Start development server
python -m uvicorn app.main:app --reload --port 8000

# Start RQ worker for background tasks
rq worker --url redis://localhost:6379 default

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_router.py -v
```

### Frontend Development (streamlit_frontend/)

```bash
cd streamlit_frontend

# Install dependencies
pip install -r requirements.txt

# Start Streamlit app
streamlit run app.py --server.port 8501

# Run frontend tests
python test_frontend.py
```

### API Testing

```bash
# Test all endpoints
python test_api.py

# Test improved upload system
python test_upload_improved.py

# Test specific endpoint with curl
curl -X GET "http://localhost:8000/health"

# Test file upload (now with async processing)
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "workspace_id=test" \
  -F "file=@sample.pdf"

# Monitor upload status
curl "http://localhost:8000/api/v1/status/{file_id}?workspace_id=test"

# View all processing statuses
curl "http://localhost:8000/api/v1/processing/status"
```

## Core Service Architecture

### Model Routing System

The system uses intelligent model routing defined in `app/config/model_routing.py`:

- **code_generation** → phi3:3.8b (low temperature, high tokens)
- **research_longform** → llama2:7b-chat (balanced settings)
- **factual_short_answer** → phi3:3.8b (low temperature, focused)
- **table_query** → phi3:3.8b (structured output optimized)
- **summarize** → phi3:3.8b (condensation focused)

Intent classification happens automatically via the ModelRouter service, with fallback to research_longform for ambiguous queries.

### Storage Architecture

- **Local Storage** - File system storage for development
- **S3 Storage** - Cloud storage for production
- **Vector Database** - FAISS indices for similarity search
- **MongoDB** - User management and metadata
- **Redis** - Task queues and caching

### AI Services Pipeline

1. **Ingest Service** (`app/services/ingest.py`) - File parsing and chunking
2. **Embeddings Service** (`app/services/embeddings.py`) - Text vectorization
3. **Vector DB Service** (`app/services/vectordb.py`) - Similarity search
4. **Web Search Service** (`app/services/web_search.py`) - External enrichment
5. **Reranker Service** (`app/services/reranker.py`) - Result ranking
6. **Summarizer Service** (`app/services/summarizer.py`) - Answer generation

## Key API Endpoints

### File Upload & Processing
- `POST /api/v1/upload` - Upload file with immediate response (HTTP 202)
- `GET /api/v1/status/{file_id}` - Get processing status and progress
- `GET /api/v1/processing/status` - View all processing statuses
- `GET /api/v1/files/{workspace_id}` - List files with processing status

### Core Operations
- `POST /api/v1/search` - Full AI search pipeline
- `GET /api/v1/file/{file_id}` - File metadata and content
- `DELETE /api/v1/file/{file_id}` - Delete file and associated data

### Authentication
- `POST /api/register` - User registration  
- `POST /api/login` - User authentication
- JWT tokens required for all protected endpoints

### System Health
- `GET /health` - Health check
- `GET /` - API information and docs

## Prerequisites for Development

### Required Services
- **Python 3.8+**
- **Redis** (localhost:6379) - For background tasks and caching
- **Ollama** (localhost:11434) - For local LLM inference
- **MongoDB** (localhost:27017) - For user management

### Model Dependencies
- **sentence-transformers** - For embeddings
- **FAISS** - For vector search
- **transformers** - For reranking models
- **Ollama models** - phi3:3.8b, llama2:7b-chat recommended

### Environment Configuration

Backend requires `.env` file with:
```env
MONGODB_URL=mongodb://localhost:27017/omnisearch
ACCESS_TOKEN_SECRET=your_secret_key
OLLAMA_HOST=http://localhost:11434
REDIS_URL=redis://localhost:6379/0
```

## File Processing Pipeline

### Improved Upload System

The system now uses a **fast local storage + async processing** approach to prevent upload timeouts and crashes:

1. **Immediate Local Storage** - Files are saved locally first for fast response
2. **Background Processing** - AI pipeline runs asynchronously after upload
3. **Real-time Status Tracking** - Monitor processing progress via API
4. **Error Recovery** - Failed processing doesn't affect file storage

### Supported Formats
- **PDF** - Full text extraction with page preservation
- **DOCX** - Microsoft Word document processing  
- **TXT** - Plain text with encoding detection
- **File Size Limit** - 10MB maximum per file

### Processing Flow
1. **Upload** - File saved to `data/uploads/{workspace_id}/` immediately
2. **Status Tracking** - Processing status saved to `data/processing_status/`
3. **Background Task** - File queued for async processing
4. **Text Extraction** - Format-specific parsers extract content
5. **Chunking** - Configurable size and overlap (1000 chars, 200 overlap)
6. **Embedding Generation** - Sentence transformers create vectors
7. **Vector Storage** - FAISS index updated with embeddings
8. **Cleanup** - Temporary files removed after processing

## Search Pipeline

### Full Search Flow
1. Query intent classification via ModelRouter
2. Vector similarity search in FAISS index
3. Optional web search enrichment
4. Result reranking with cross-encoders
5. Context assembly and citation tracking
6. LLM-powered summarization with provenance

### Search Configuration
- Configurable chunk retrieval (top_k)
- Reranking enable/disable
- Web search integration toggle
- Temperature and token limits per intent

## Testing Strategy

### Backend Tests
```bash
# Run all tests
pytest tests/

# Test specific service
pytest tests/test_router.py

# Test search pipeline
pytest tests/test_search_shape.py
```

### Integration Testing
```bash
# Full system test
python demo_full_stack.py --demo

# API endpoint testing
python test_api.py

# Test improved upload system
python test_upload_improved.py
```

## Development Guidelines

### Adding New Services
1. Create service class in `app/services/`
2. Implement async methods for scalability
3. Add configuration to `app/config/`
4. Wire into API endpoints in `app/api/v1/`
5. Add comprehensive tests

### Model Integration
1. Update `app/config/model_routing.py` with new intents
2. Add model profiles with appropriate parameters
3. Update routing logic in `app/services/model_router.py`
4. Test with representative queries

### Storage Backends
- Implement storage interface in `app/services/storage.py`
- Support both local filesystem and S3-compatible storage
- Handle file validation and security

## Troubleshooting Common Issues

### File Upload Problems
- **Upload Timeouts**: Now resolved with immediate local storage
- **Processing Crashes**: Files are saved even if processing fails
- **Status Monitoring**: Use `/api/v1/status/{file_id}` to track progress
- **Large Files**: Check 10MB size limit and supported formats (.pdf, .docx, .txt)

### Processing Issues
- **Stuck Processing**: Check `data/processing_status/` directory for status files
- **Background Tasks**: Verify FastAPI background tasks are running
- **Storage Space**: Ensure adequate disk space in `data/uploads/` and `data/processing_status/`
- **File Permissions**: Check write permissions for data directories

### Service Connection Failures
- Verify Redis: `redis-cli ping` (optional for new system)
- Check Ollama: `curl http://localhost:11434/api/tags`
- Test MongoDB: `mongosh --eval "db.runCommand('ping')"`

### Performance Issues
- Monitor vector index size and RAM usage
- Check processing status files for bottlenecks
- Verify Ollama model loading and inference times
- Profile embedding generation bottlenecks
- Clean up old status files periodically

### Authentication Problems
- Verify JWT token validity and expiration
- Check middleware configuration
- Validate environment variables

## Recent Improvements

### Enhanced Upload System (Latest)

The upload system has been completely redesigned to address performance and reliability issues:

**Key Improvements:**
- ⚡ **Fast Uploads** - Files saved locally first for immediate response
- 🔄 **Async Processing** - AI pipeline runs in background without blocking
- 📊 **Real-time Status** - Track processing progress with detailed status API
- 🛡️ **Error Recovery** - File storage succeeds even if AI processing fails
- 📈 **Better Monitoring** - Comprehensive status tracking and progress reporting
- 🧹 **Automatic Cleanup** - Temporary files cleaned up after processing

**Testing:** Run `python test_upload_improved.py` to verify the new system

This system is designed for rapid development and deployment of AI-powered document search applications, with emphasis on modularity, scalability, and intelligent routing of different query types to appropriate models.
