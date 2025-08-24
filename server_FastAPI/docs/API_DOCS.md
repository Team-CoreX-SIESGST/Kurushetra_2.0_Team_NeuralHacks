# OmniSearch AI API Documentation

## Overview

OmniSearch AI is an AI-powered orchestrator that ingests user files, enriches with web results, routes tasks to the right model via Ollama, and returns provenance-backed answers.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints require Bearer token authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

Unauthorized requests will return a 401 status code.

## Endpoints

### 1. File Upload

#### POST /api/v1/upload

Upload a file and enqueue indexing job.

**Form Data:**
- `workspace_id` (string, required): Workspace identifier
- `file` (file, required): File to upload (PDF, DOCX, TXT)
- `file_id` (string, optional): Custom file ID

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "document.pdf",
  "status": "uploaded",
  "message": "Indexing queued",
  "details": {
    "chunks_created": 15,
    "total_characters": 5000,
    "vector_count": 15
  }
}
```

**Status Codes:**
- 200: Success
- 202: File uploaded but indexing failed
- 400: Bad request
- 401: Unauthorized
- 500: Internal server error

### 2. File Status

#### GET /api/v1/status/{file_id}

Get the processing status of a file.

**Query Parameters:**
- `workspace_id` (string, required): Workspace identifier

**Response:**
```json
{
  "file_id": "uuid-string",
  "workspace_id": "workspace-123",
  "status": "processed",
  "file_info": {
    "file_id": "uuid-string",
    "filename": "document.pdf",
    "workspace_id": "workspace-123",
    "status": "stored",
    "storage_path": "workspace-123/uuid-string.pdf",
    "storage_type": "local",
    "file_size": 1024000,
    "storage_time": "2024-01-01T00:00:00"
  },
  "last_checked": "2024-01-01T00:00:00"
}
```

### 3. Search

#### POST /api/v1/search

Search documents using the full AI pipeline.

**Request Body:**
```json
{
  "workspace_id": "workspace-123",
  "query": "Summarize methods used",
  "top_k": 10,
  "include_web": true,
  "rerank": true,
  "summarize": true
}
```

**Response:**
```json
{
  "answer": "Based on the available sources [SRC_1], the methods used include...",
  "confidence": 0.85,
  "sources": [
    {
      "file_id": "uuid-string",
      "filename": "document.pdf",
      "page": 1,
      "snippet": "The research methodology employed...",
      "score": 0.92,
      "url": ""
    }
  ],
  "raw_chunks": [
    {
      "id": "uuid-string_chunk_0",
      "text": "The research methodology employed...",
      "score": 0.92
    }
  ],
  "processing_time": 2.5,
  "metadata": {
    "intent": "research_longform",
    "model_used": "llama2",
    "search_type": "full_pipeline",
    "vector_results": 10,
    "web_results": 3,
    "reranked": true,
    "summarized": true
  }
}
```

**Search Parameters:**
- `workspace_id` (string, required): Workspace identifier
- `query` (string, required): Search query
- `top_k` (integer, default: 10): Number of results to return
- `include_web` (boolean, default: true): Include web search results
- `rerank` (boolean, default: true): Apply reranking
- `summarize` (boolean, default: true): Generate final summary

### 4. Simple Search

#### GET /api/v1/search/simple

Simple search without full AI pipeline.

**Query Parameters:**
- `workspace_id` (string, required): Workspace identifier
- `query` (string, required): Search query
- `top_k` (integer, default: 5): Number of results to return

**Response:**
```json
{
  "query": "search term",
  "workspace_id": "workspace-123",
  "results": [
    {
      "id": "uuid-string_chunk_0",
      "text": "Search result text...",
      "score": 0.85,
      "file_id": "uuid-string",
      "filename": "document.pdf",
      "page": 1
    }
  ],
  "total_results": 5,
  "search_time": "2024-01-01T00:00:00"
}
```

### 5. Search Statistics

#### GET /api/v1/search/stats/{workspace_id}

Get search statistics for a workspace.

**Response:**
```json
{
  "workspace_id": "workspace-123",
  "stats": {
    "workspace_id": "workspace-123",
    "vector_count": 150,
    "index_dimension": 384,
    "last_updated": "2024-01-01T00:00:00"
  },
  "retrieved_at": "2024-01-01T00:00:00"
}
```

### 6. File Information

#### GET /api/v1/file/{file_id}

Get file information and metadata.

**Query Parameters:**
- `workspace_id` (string, required): Workspace identifier

**Response:**
```json
{
  "file_id": "uuid-string",
  "workspace_id": "workspace-123",
  "file_info": {
    "file_id": "uuid-string",
    "filename": "document.pdf",
    "workspace_id": "workspace-123",
    "status": "stored",
    "storage_path": "workspace-123/uuid-string.pdf",
    "storage_type": "local",
    "file_size": 1024000,
    "created_time": "2024-01-01T00:00:00",
    "modified_time": "2024-01-01T00:00:00",
    "retrieval_time": "2024-01-01T00:00:00"
  },
  "retrieved_at": "2024-01-01T00:00:00"
}
```

### 7. File Page

#### GET /api/v1/file/{file_id}/page/{page_number}

Get specific page content from a file.

**Path Parameters:**
- `file_id` (string, required): File identifier
- `page_number` (integer, required): Page number (1-based)

**Query Parameters:**
- `workspace_id` (string, required): Workspace identifier

**Response:**
```json
{
  "file_id": "uuid-string",
  "workspace_id": "workspace-123",
  "page_number": 1,
  "page_content": "Page content text...",
  "chunks": [
    {
      "chunk_id": "uuid-string_chunk_0",
      "text": "Chunk text...",
      "chunk_index": 0,
      "start_char": 0,
      "end_char": 1000
    }
  ],
  "total_chunks": 3,
  "retrieved_at": "2024-01-01T00:00:00"
}
```

### 8. File Chunks

#### GET /api/v1/file/{file_id}/chunks

Get chunks from a file, optionally filtered by page.

**Query Parameters:**
- `workspace_id` (string, required): Workspace identifier
- `page` (integer, optional): Filter by page number
- `limit` (integer, default: 50): Maximum number of chunks to return

**Response:**
```json
{
  "file_id": "uuid-string",
  "workspace_id": "workspace-123",
  "chunks": [
    {
      "chunk_id": "uuid-string_chunk_0",
      "text": "Chunk text...",
      "page": 1,
      "chunk_index": 0,
      "start_char": 0,
      "end_char": 1000,
      "score": 0.85,
      "timestamp": "2024-01-01T00:00:00"
    }
  ],
  "total_chunks": 15,
  "page_filter": null,
  "limit_applied": 50,
  "retrieved_at": "2024-01-01T00:00:00"
}
```

### 9. File Download

#### GET /api/v1/file/{file_id}/download

Download a file.

**Query Parameters:**
- `workspace_id` (string, required): Workspace identifier

**Response:**
- For local storage: File download
- For S3 storage: JSON with presigned URL

```json
{
  "download_url": "https://presigned-url...",
  "expires_in": "1 hour",
  "message": "Use the download_url to access the file"
}
```

### 10. File Metadata

#### GET /api/v1/file/{file_id}/metadata

Get comprehensive metadata for a file.

**Query Parameters:**
- `workspace_id` (string, required): Workspace identifier

**Response:**
```json
{
  "file_id": "uuid-string",
  "workspace_id": "workspace-123",
  "storage_info": {
    "file_id": "uuid-string",
    "filename": "document.pdf",
    "workspace_id": "workspace-123",
    "status": "stored",
    "storage_path": "workspace-123/uuid-string.pdf",
    "storage_type": "local",
    "file_size": 1024000,
    "created_time": "2024-01-01T00:00:00",
    "modified_time": "2024-01-01T00:00:00",
    "retrieval_time": "2024-01-01T00:00:00"
  },
  "vector_stats": {
    "total_chunks": 15,
    "total_pages": 5,
    "total_characters": 15000,
    "average_chunk_size": 1000
  },
  "page_statistics": {
    "1": {
      "chunk_count": 3,
      "character_count": 3000
    }
  },
  "chunk_distribution": {
    "chunks_per_page": {
      "1": 3,
      "2": 3,
      "3": 3,
      "4": 3,
      "5": 3
    }
  },
  "retrieved_at": "2024-01-01T00:00:00"
}
```

### 11. File Management

#### DELETE /api/v1/file/{file_id}

Delete a file and its associated data.

**Query Parameters:**
- `workspace_id` (string, required): Workspace identifier

**Response:**
```json
{
  "file_id": "uuid-string",
  "workspace_id": "workspace-123",
  "status": "deleted",
  "message": "File deleted successfully",
  "deleted_at": "2024-01-01T00:00:00"
}
```

#### GET /api/v1/files/{workspace_id}

List all files in a workspace.

**Response:**
```json
{
  "workspace_id": "workspace-123",
  "files": [
    {
      "file_id": "uuid-string",
      "filename": "document.pdf",
      "workspace_id": "workspace-123",
      "storage_path": "workspace-123/uuid-string.pdf",
      "file_size": 1024000,
      "last_modified": "2024-01-01T00:00:00",
      "storage_type": "local"
    }
  ],
  "total_files": 1,
  "retrieved_at": "2024-01-01T00:00:00"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## File Formats

Supported file formats:
- PDF (.pdf)
- Microsoft Word (.docx)
- Plain Text (.txt)

## Search Pipeline

The search endpoint implements a comprehensive AI pipeline:

1. **Intent Classification**: Routes queries to appropriate models
2. **Vector Search**: Finds relevant document chunks
3. **Web Enrichment**: Adds web search results
4. **Reranking**: Improves result relevance
5. **Summarization**: Generates final answer with citations

## Model Routing

The system automatically routes queries to appropriate models based on intent:
- `code_generation`: CodeLlama
- `research_longform`: Llama2 13B
- `factual_short_answer`: Llama2 7B
- `table_query`: Llama2 7B
- `image_analysis`: LLaVA
- `summarize`: Llama2 7B

## Environment Variables

Required environment variables:

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

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env` file

3. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Access the API documentation at `/docs`

5. Start Redis for background jobs:
   ```bash
   redis-server
   ```

6. Start RQ worker:
   ```bash
   rq worker --url redis://localhost:6379 default
   ```

## Testing

Test the API with the provided demo script:

```bash
# Upload sample PDF
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "workspace_id=demo" \
  -F "file=@sample_data/sample.pdf"

# Run search
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id":"demo","query":"Summarize methods used","top_k":10,"include_web":true}'
```

## Support

For questions and support, please refer to the project documentation or create an issue in the repository.
