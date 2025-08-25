# File Processing & RAG System

A comprehensive file processing system that can extract data from various file formats, convert them to JSON, and generate AI-powered summaries using Google's Gemini API.

## Features

### 🔧 File Processing
- **Multiple Format Support**: PDF, Word Documents, Excel, PowerPoint, CSV, Text, JSON, XML, HTML, Markdown, and Images (with OCR)
- **Smart Data Extraction**: Automatically extracts text, tables, metadata, and structured data
- **JSON Conversion**: All extracted data is standardized into JSON format
- **Error Handling**: Robust error handling with fallback options

### 🤖 RAG System with Gemini API
- **Multiple Summary Types**: General, Key Points, Technical, Executive, and Analysis summaries
- **Smart Context Preparation**: Optimizes content for AI processing
- **Fallback Summaries**: Basic summaries when AI is unavailable
- **Content Analysis**: Statistics and metadata about processed content

### 🚀 FastAPI Web Server
- **RESTful API**: Clean, documented endpoints
- **File Upload**: Secure file handling with validation
- **Interactive Documentation**: Automatic Swagger/OpenAPI docs
- **Health Monitoring**: System status and API health checks

## Supported File Formats

| Format | Extensions | Features |
|--------|------------|----------|
| **PDF** | `.pdf` | Text extraction, tables, metadata |
| **Word** | `.docx`, `.doc` | Paragraphs, tables, document properties |
| **Excel** | `.xlsx`, `.xls` | Multiple sheets, data analysis, statistics |
| **PowerPoint** | `.pptx`, `.ppt` | Slides content, speaker notes |
| **CSV** | `.csv` | Data parsing, statistics, encoding detection |
| **Text** | `.txt` | Full text with statistics |
| **JSON** | `.json` | Structured data parsing |
| **XML** | `.xml` | Hierarchical data conversion |
| **HTML** | `.html`, `.htm` | Content extraction, links, metadata |
| **Markdown** | `.md` | Parsed content and structure |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.tiff` | OCR text extraction |

## Installation

### Quick Setup (Recommended)

1. **Clone or download the project**
2. **Run the setup script**:
   ```bash
   python setup.py
   ```
   This will automatically:
   - Check Python version compatibility
   - Create a virtual environment
   - Install all dependencies
   - Create necessary directories
   - Set up configuration files

### Manual Setup

1. **Python Requirements**: Python 3.8 or higher

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required: Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Optional: File Processing
MAX_FILE_SIZE_MB=100
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Add it to your `.env` file

## Usage

### Starting the Server

```bash
# Method 1: Direct execution
python main.py

# Method 2: Using uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

#### 1. Get Supported Formats
```http
GET /supported-formats
```

#### 2. Process File (Extract to JSON)
```http
POST /process-file
Content-Type: multipart/form-data

file: [your-file]
```

#### 3. Process and Summarize
```http
POST /process-and-summarize
Content-Type: multipart/form-data

file: [your-file]
```

#### 4. Summarize JSON Data
```http
POST /summarize-json
Content-Type: application/json

{
  "your": "json data here"
}
```

#### 5. Health Check
```http
GET /health
```

### Interactive Documentation

Once the server is running, visit:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Example Usage

### Python Client Example

```python
import requests

# Process a file and get summary
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/process-and-summarize', 
        files=files
    )
    
    result = response.json()
    print("Summary:", result['summary'])
    print("Extracted Data:", result['extracted_data'])
```

### cURL Example

```bash
# Process a file
curl -X POST "http://localhost:8000/process-file" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

## Output Examples

### Extracted JSON Structure
```json
{
  "content_type": "pdf",
  "text_content": [
    {
      "page": 1,
      "content": "Document content here..."
    }
  ],
  "document_metadata": {
    "pages": 5,
    "metadata": {...}
  },
  "file_metadata": {
    "original_filename": "document.pdf",
    "file_size": 1024000,
    "processed_at": "2024-01-15T10:30:00"
  }
}
```

### AI Summary Structure
```json
{
  "summaries": {
    "general": "Comprehensive overview of the document...",
    "key_points": "• Main point 1\n• Main point 2...",
    "executive": "High-level business summary...",
    "analysis": "Content analysis and insights..."
  },
  "metadata": {
    "generated_at": "2024-01-15T10:30:00",
    "content_type": "pdf",
    "source_file": "document.pdf"
  },
  "content_stats": {
    "word_count": 1500,
    "character_count": 8500
  }
}
```

## Dependencies

### Core Dependencies
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **aiohttp**: HTTP client for API calls

### File Processing Libraries
- **PyPDF2/pdfplumber**: PDF processing
- **python-docx**: Word documents
- **pandas**: Excel and CSV processing
- **python-pptx**: PowerPoint presentations
- **Pillow/pytesseract**: Image OCR
- **BeautifulSoup**: HTML parsing
- **lxml**: XML processing
- **markdown**: Markdown processing

### Optional Dependencies
- **Tesseract OCR**: Required for image text extraction
  - Windows: Download from [GitHub](https://github.com/tesseract-ocr/tesseract)
  - Linux: `sudo apt-get install tesseract-ocr`
  - Mac: `brew install tesseract`

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Set the API key in your `.env` file
   - Ensure the file is in the same directory as `main.py`

2. **"Tesseract not found"**
   - Install Tesseract OCR for image processing
   - OCR functionality will be disabled without it

3. **Import errors for file processing libraries**
   - Run `pip install -r requirements.txt`
   - Some libraries are optional and will gracefully degrade

4. **Large file processing fails**
   - Adjust `MAX_FILE_SIZE_MB` in `.env`
   - Ensure sufficient system memory

## Architecture

```
new_server/
├── main.py              # FastAPI application
├── file_processor.py    # File processing logic
├── rag_system.py        # RAG and Gemini integration
├── requirements.txt     # Python dependencies
├── setup.py            # Automated setup script
├── .env.example        # Environment template
├── README.md           # This file
├── uploads/            # Temporary file storage
├── extracted_data/     # JSON output files
├── processed_data/     # Files with summaries
└── logs/               # Application logs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Check the logs in the `logs/` directory
4. Open an issue on GitHub

---

**Made with ❤️ for document processing and AI integration**
