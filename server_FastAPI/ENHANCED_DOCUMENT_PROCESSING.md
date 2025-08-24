# Enhanced Document Processing System 🚀

**Gemini-Powered RAG with Web Enhancement for OmniSearch AI**

## Overview

The Enhanced Document Processing System is a comprehensive solution that converts various document formats to JSON, generates intelligent summaries using Google's Gemini AI, performs related web searches, and produces enhanced summaries with contextual insights.

### Key Features

- ✅ **Multi-format Support**: .txt, .md, .pdf, .docx, .rtf, .odt, .csv
- ✅ **Gemini-Only AI**: Removed all Llama dependencies, using Google Gemini exclusively  
- ✅ **Intelligent RAG**: Retrieval-Augmented Generation for comprehensive document understanding
- ✅ **Web Enhancement**: Automatic web search for related content and context
- ✅ **Batch Processing**: Handle multiple documents with comparative analysis
- ✅ **Structured JSON Output**: Consistent, machine-readable document representation

## Architecture

### 🔄 Complete Workflow

```
📄 Document Upload
    ↓
📋 Document to JSON Conversion
    ↓
🧠 Gemini RAG Summarization
    ↓
🏷️ Search Tag Generation
    ↓
🌐 Web Search for Related Content
    ↓
🚀 Enhanced Summary Generation
    ↓
📊 Results with Context & Insights
```

### 🛠️ Core Services

1. **DocumentConverterService** - Multi-format document to JSON conversion
2. **GeminiRAGService** - AI-powered document analysis and summarization
3. **EnhancedSummaryService** - Complete workflow orchestration with web enhancement
4. **WebSearchService** - Intelligent web search for related content

## API Endpoints

Base URL: `/api/v1/enhanced-documents/`

### 🔗 Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/process/single` | POST | Complete enhanced workflow for single document |
| `/process/batch` | POST | Batch processing with comparative analysis (max 10 files) |
| `/convert/json` | POST | Document to JSON conversion only |
| `/summarize/basic` | POST | Basic Gemini RAG summarization |
| `/tags/generate` | POST | Generate searchable tags |
| `/formats/supported` | GET | List supported formats and capabilities |
| `/health` | GET | Service health check |
| `/` | GET | Service information |

## 📄 Supported Document Formats

### Text Formats
- **.txt** - Plain text files with multiple encoding support
- **.md** - Markdown with header extraction and code block detection

### Office Documents  
- **.pdf** - PDF with metadata extraction and page-by-page processing
- **.docx** - Microsoft Word with style recognition and document properties
- **.rtf** - Rich Text Format with formatting preservation
- **.odt** - OpenDocument Text format

### Data Files
- **.csv** - Comma-separated values with data type analysis

## 🧠 AI-Powered Features

### Gemini RAG Capabilities
- **Comprehensive Summarization**: Multi-paragraph intelligent summaries
- **Key Topic Extraction**: Automatic identification of main themes
- **Insight Generation**: Actionable insights and findings
- **Concept Mapping**: Main concepts and relationships
- **Query Suggestions**: Potential questions users might ask

### Web Enhancement
- **Intelligent Tag Generation**: AI-powered search tag creation
- **Related Content Discovery**: Automatic web search for context
- **Contextual Insights**: How document relates to broader topics
- **Practical Applications**: Real-world use cases and applications

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+**
2. **Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Required Dependencies** - Install via requirements.txt

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_gemini_api_key_here"

# Run the server
python app/main.py
```

### Quick Demo

```bash
# Run the comprehensive demo
python enhanced_document_demo.py
```

## 📋 Example Usage

### Single Document Processing

```python
import requests

# Upload and process a document
with open("document.pdf", "rb") as file:
    response = requests.post(
        "http://localhost:8000/api/v1/enhanced-documents/process/single",
        files={"file": file}
    )

result = response.json()
print(result["data"]["enhanced_summary"]["enhanced_summary"])
```

### Batch Processing with Comparative Analysis

```python
files = [
    ("files", open("doc1.txt", "rb")),
    ("files", open("doc2.pdf", "rb")),
    ("files", open("doc3.md", "rb"))
]

response = requests.post(
    "http://localhost:8000/api/v1/enhanced-documents/process/batch",
    files=files
)

# Get comparative analysis
comparative = response.json()["data"]["comparative_analysis"]
print(comparative["comparative_summary"])
```

## 📊 Sample Response Structure

### Enhanced Summary Response

```json
{
  "success": true,
  "message": "Document processed successfully through enhanced workflow",
  "data": {
    "document_id": "uuid-here",
    "filename": "example.pdf",
    "status": "success",
    "document_summary": {
      "summary": "Comprehensive document summary...",
      "key_topics": ["topic1", "topic2", "topic3"],
      "insights": ["insight1", "insight2"],
      "confidence": 0.85
    },
    "web_research": {
      "search_tags": ["tag1", "tag2", "tag3"],
      "website_urls": [
        {
          "url": "https://example.com",
          "title": "Related Article",
          "snippet": "Description...",
          "relevance_score": 0.9
        }
      ],
      "total_urls_found": 5
    },
    "enhanced_summary": {
      "enhanced_summary": "Comprehensive summary with web context...",
      "contextual_insights": ["insight1", "insight2"],
      "related_topics": ["broader_topic1", "broader_topic2"],
      "practical_applications": ["application1", "application2"],
      "further_research_suggestions": ["suggestion1", "suggestion2"],
      "confidence_score": 0.88,
      "web_sources_used": 5
    },
    "processing_metadata": {
      "processing_time": 12.34,
      "workflow_steps": ["Step1", "Step2", "Step3"],
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
ENHANCED_PROCESSING_ENABLED=true
GEMINI_TIMEOUT_SECONDS=30
WEB_SEARCH_MAX_RESULTS=10
```

### Settings

Key configuration options in `app/settings.py`:

```python
# Enhanced document processing
enhanced_processing_enabled: bool = True
gemini_timeout_seconds: int = 30
web_search_max_results: int = 10

# File processing limits
max_file_size_mb: int = 10
max_concurrency: int = 1

# Web search settings
enable_web_search: bool = True
```

## 📈 Performance & Limits

### Processing Limits
- **Single File**: Up to 10MB
- **Batch Processing**: Maximum 10 files per request
- **Document Length**: Up to 4,000 characters for Gemini processing
- **Web Results**: Up to 10 URLs per document

### Performance Metrics
- **Document Conversion**: ~1-2 seconds
- **Gemini Summarization**: ~5-10 seconds  
- **Web Search**: ~3-5 seconds
- **Total Workflow**: ~10-20 seconds per document

## 🛡️ Security & Privacy

### Data Handling
- **No Data Storage**: Documents are processed in memory only
- **Secure Processing**: Files are automatically cleaned up after processing
- **API Security**: Rate limiting and input validation implemented
- **Privacy**: Content is only sent to Gemini for AI processing

### Rate Limiting
- **General Requests**: 20 per minute, 100 per hour
- **File Uploads**: 3 per minute, 10 per hour
- **Concurrent Processing**: Maximum 2 per user

## 🔍 Monitoring & Health Checks

### Health Endpoint
```bash
GET /api/v1/enhanced-documents/health
```

Response includes:
- Service status
- Gemini connectivity
- Processing capabilities
- System resources

### Service Statistics
- Processing success rates
- Average processing times  
- Error rates and types
- Resource utilization

## 🚫 Removed Features

This system completely removes Llama dependencies:

### ❌ Removed
- Ollama integration
- Local Llama model support
- Llama-based summarization
- Local model hosting requirements

### ✅ Replaced With
- Google Gemini API integration
- Cloud-based AI processing
- Enhanced web search integration
- Improved response quality

## 🐛 Troubleshooting

### Common Issues

1. **Gemini API Key Not Working**
   ```bash
   # Verify your API key
   export GEMINI_API_KEY="your_key_here"
   ```

2. **Document Conversion Failures**
   - Check file format support
   - Verify file isn't corrupted
   - Ensure file size under 10MB

3. **Web Search Not Working**
   - Check internet connectivity
   - Verify rate limits not exceeded
   - Review search tag generation

4. **Processing Timeouts**
   - Increase `GEMINI_TIMEOUT_SECONDS`
   - Reduce document size
   - Check system resources

## 📚 API Documentation

Full interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Create an issue on GitHub
4. Contact the development team

---

**Built with ❤️ using Google Gemini AI and FastAPI**
