# OmniSearch AI - Gemini-Only Backend Implementation

## Overview

OmniSearch AI is an AI-powered orchestrator that ingests user files, enriches with web results, and uses Google's Gemini AI for all processing. This repository contains the simplified FastAPI backend implementation focused exclusively on Gemini AI.

## Features

- **File Ingestion**: Support for PDF, DOCX, TXT, MD, RTF, ODT, and CSV files
- **Gemini AI Processing**: All AI tasks handled by Google's Gemini 2.0 Flash
- **Enhanced Document Processing**: Complete workflow with web enhancement
- **Web Enrichment**: Integration with web search to enhance results
- **Simplified Architecture**: No complex vector databases or model routing
- **Local Storage**: Simple file storage system for uploaded documents

## Architecture

The system follows a simplified service-oriented architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │  Service Layer  │    │  Storage Layer  │
│                 │    │                 │    │                 │
│ • Uploads       │───▶│ • Gemini RAG    │───▶│ • Local Storage │
│ • Search        │    │ • Document      │    │ • File System   │
│ • Files         │    │   Converter     │    │ • Metadata      │
│ • Enhanced      │    │ • Web Search    │    └─────────────────┘
│   Documents     │    │ • Enhanced      │
└─────────────────┘    │   Summary       │
                       └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key
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
python run_server.py
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

# Gemini AI (Required)
GEMINI_API_KEY=your_gemini_api_key

# Server settings
SERVER_PORT=8000
```

## API Endpoints

### Core Endpoints

#### File Upload
- `POST /api/v1/upload` - Upload files for Gemini processing

#### Search
- `POST /api/v1/search` - Gemini-powered search with web enhancement
- `GET /api/v1/search/simple` - Simple Gemini search
- `GET /api/v1/search/stats/{workspace_id}` - Search statistics

#### File Management
- `GET /api/v1/file/{file_id}` - Get file information
- `GET /api/v1/file/{file_id}/download` - Download file
- `GET /api/v1/file/{file_id}/metadata` - Get comprehensive metadata
- `DELETE /api/v1/file/{file_id}` - Delete file
- `GET /api/v1/files/{workspace_id}` - List workspace files

#### Enhanced Document Processing
- `POST /api/v1/enhanced-documents/process/single` - Process single document
- `POST /api/v1/enhanced-documents/process/batch` - Batch processing
- `POST /api/v1/enhanced-documents/convert/json` - Convert to JSON
- `POST /api/v1/enhanced-documents/summarize/basic` - Basic summarization

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
    "summarize": true
  }'
```

### Enhanced Document Processing

```bash
curl -X POST "http://localhost:8000/api/v1/enhanced-documents/process/single" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@document.pdf"
```

## What's Different

### ✅ What We Kept
- **Gemini AI Integration**: All AI processing uses Google Gemini
- **Enhanced Document Processing**: Complete workflow with web enhancement
- **File Management**: Upload, storage, and retrieval
- **Web Search**: Integration for content enrichment
- **Authentication**: JWT-based user management

### ❌ What We Removed
- **Vector Databases**: No more FAISS or complex embeddings
- **Model Routing**: No more Ollama or local model selection
- **Queue Systems**: No more Redis queues or background workers
- **Complex Processing**: No more chunking, reranking, or embeddings
- **Legacy Services**: Removed unused AI services and dependencies

## Project Structure

```
server_FastAPI/
├── app/
│   ├── api/v1/           # API endpoints (simplified)
│   ├── config/           # Configuration and settings
│   ├── controllers/      # Business logic controllers
│   ├── middlewares/      # Authentication and middleware
│   ├── models/           # Data models
│   ├── routes/           # Route definitions
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Core services (Gemini-focused)
│   └── utils/            # Utility functions
├── docs/                 # API documentation
├── requirements.txt      # Python dependencies (simplified)
└── README.md            # This file
```

## Core Services

### Gemini Services
- **GeminiService**: Core Gemini AI interactions
- **GeminiRAGService**: RAG implementation with Gemini
- **EnhancedSummaryService**: Complete document workflow

### Document Processing
- **DocumentConverterService**: Multi-format document conversion
- **WebSearchService**: Web content enrichment

### Storage
- **StorageService**: Simplified local file storage

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

## Troubleshooting

### Common Issues

1. **Gemini API Key Not Working**
   - Verify your API key in `.env` file
   - Check Gemini API quota and limits

2. **File Upload Failures**
   - Check file format support
   - Verify file size limits (10MB max)
   - Ensure storage directory permissions

3. **Authentication Errors**
   - Verify JWT tokens are valid
   - Check token expiration
   - Ensure middleware is properly configured

## Performance

- **File Processing**: ~1-2 seconds for conversion
- **Gemini Processing**: ~5-10 seconds for summarization
- **Web Search**: ~3-5 seconds for enrichment
- **Total Workflow**: ~10-20 seconds per document

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

---

**Built with ❤️ using Google Gemini AI and FastAPI**
