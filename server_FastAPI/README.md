# OmniSearch AI - Backend Implementation

## Overview

OmniSearch AI is an AI-powered orchestrator that ingests user files, enriches with web results, routes tasks to the right model via Ollama, and returns provenance-backed answers. This repository contains the FastAPI backend implementation.

## Features

- **File Ingestion**: Support for PDF, DOCX, and TXT files with automatic chunking and vectorization
- **AI Model Routing**: Intelligent routing of queries to appropriate models based on intent classification
- **Vector Search**: FAISS-based similarity search with configurable chunk sizes and overlap
- **Web Enrichment**: Integration with web search to enhance results with external information
- **Reranking**: Cross-encoder based reranking for improved search relevance
- **Summarization**: LLM-powered summarization with source citations
- **Storage**: Flexible storage backend supporting both local filesystem and S3
- **Authentication**: JWT-based authentication with middleware protection

## Architecture

The system follows a modular service-oriented architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │  Service Layer  │    │  Storage Layer  │
│                 │    │                 │    │                 │
│ • Uploads       │───▶│ • Model Router  │───▶│ • Local Storage │
│ • Search        │    │ • Embeddings    │    │ • S3 Storage    │
│ • Files        │    │ • Vector DB     │    │ • Vector DB     │
└─────────────────┘    │ • Reranker      │    └─────────────────┘
                       │ • Summarizer    │
                       │ • Web Search    │
                       │ • Ingest        │
                       └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- Redis server
- Ollama (for local LLM inference)
- MongoDB (for user management)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd server_FastAPI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp example_env.txt .env
# Edit .env with your configuration
```

4. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

5. Start Redis for background jobs:
```bash
redis-server
```

6. Start RQ worker:
```bash
rq worker --url redis://localhost:6379 default
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017/omnisearch

# Authentication
ACCESS_TOKEN_SECRET=your_access_token_secret
REFRESH_TOKEN_SECRET=your_refresh_token_secret

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# S3 (optional)
S3_ENDPOINT=your_s3_endpoint
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_BUCKET=omnisea-uploads

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector Database
VECTOR_DB_TYPE=faiss
HUGGINGFACE_API_TOKEN=your_token

# OpenAI (optional)
OPENAI_API_KEY=your_openai_key

# Ollama
OLLAMA_HOST=http://localhost:11434
LLAMA_LOCAL_PATH=path_to_local_models

# Auth
AUTH_PUBLIC_KEY_URL=your_auth_public_key_url
```

## API Endpoints

### Authentication
All endpoints require Bearer token authentication in the Authorization header.

### Core Endpoints

#### File Upload
- `POST /api/v1/upload` - Upload and index files

#### Search
- `POST /api/v1/search` - Full AI-powered search pipeline
- `GET /api/v1/search/simple` - Simple vector search
- `GET /api/v1/search/stats/{workspace_id}` - Search statistics

#### File Management
- `GET /api/v1/file/{file_id}` - Get file information
- `GET /api/v1/file/{file_id}/page/{page_number}` - Get specific page content
- `GET /api/v1/file/{file_id}/chunks` - Get file chunks
- `GET /api/v1/file/{file_id}/download` - Download file
- `GET /api/v1/file/{file_id}/metadata` - Get comprehensive metadata
- `DELETE /api/v1/file/{file_id}` - Delete file
- `GET /api/v1/files/{workspace_id}` - List workspace files

#### Status
- `GET /api/v1/status/{file_id}` - Get file processing status

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Usage Examples

### File Upload

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "workspace_id=demo" \
  -F "file=@sample.pdf"
```

### Search

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "demo",
    "query": "Summarize the main findings",
    "top_k": 10,
    "include_web": true,
    "rerank": true,
    "summarize": true
  }'
```

### Demo Script

Use the provided demo script to test all functionality:

```bash
chmod +x demo_script.sh
./demo_script.sh -t your_auth_token
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## Model Configuration

The system supports multiple AI models with automatic routing:

| Intent | Model | Use Case |
|--------|-------|----------|
| `code_generation` | CodeLlama 7B | Code generation and analysis |
| `research_longform` | Llama2 13B | Research and long-form content |
| `factual_short_answer` | Llama2 7B | Quick factual questions |
| `table_query` | Llama2 7B | Data analysis and table queries |
| `image_analysis` | LLaVA 7B | Image understanding |
| `summarize` | Llama2 7B | Content summarization |

## File Processing

### Supported Formats
- **PDF**: Full text extraction with page preservation
- **DOCX**: Microsoft Word document processing
- **TXT**: Plain text with encoding detection

### Chunking Strategy
- Configurable chunk size (default: 1000 characters)
- Overlapping chunks for context preservation
- Sentence boundary-aware splitting
- Page-level metadata preservation

## Performance Considerations

- **Embeddings**: Uses lightweight sentence-transformers for fast inference
- **Vector Search**: FAISS index for efficient similarity search
- **Caching**: Redis-based caching for frequently accessed data
- **Async Processing**: Non-blocking I/O for improved throughput
- **Batch Operations**: Support for bulk processing operations

## Development

### Project Structure

```
server_FastAPI/
├── app/
│   ├── api/v1/           # API endpoints
│   ├── config/           # Configuration and settings
│   ├── controllers/      # Business logic controllers
│   ├── middlewares/      # Authentication and middleware
│   ├── models/           # Data models
│   ├── routes/           # Route definitions
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Core AI services
│   └── utils/            # Utility functions
├── docs/                 # API documentation
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Adding New Services

1. Create service class in `app/services/`
2. Implement required methods
3. Add to appropriate API endpoints
4. Write tests in `tests/`
5. Update documentation

### Adding New Models

1. Update `app/config/model_routing.py`
2. Add model profile with capabilities
3. Update routing logic if needed
4. Test with sample queries

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama is running: `ollama serve`
   - Check `OLLAMA_HOST` in environment variables

2. **Vector Database Errors**
   - Verify FAISS installation: `pip install faiss-cpu`
   - Check disk space for index storage

3. **Authentication Errors**
   - Verify JWT tokens are valid
   - Check token expiration
   - Ensure middleware is properly configured

4. **File Upload Failures**
   - Check file format support
   - Verify storage permissions
   - Check available disk space

### Logs

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Check the API documentation at `/docs`
- Review the test suite for usage examples
- Create an issue in the repository
- Contact the development team

## Roadmap

- [ ] Multi-modal support (images, audio)
- [ ] Advanced caching strategies
- [ ] Real-time collaboration features
- [ ] Enhanced security features
- [ ] Performance monitoring and metrics
- [ ] Kubernetes deployment support
