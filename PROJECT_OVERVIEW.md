# OmniSearch AI - Complete Project Overview

## 🎯 Project Summary

OmniSearch AI is a comprehensive AI-powered document search and analysis system that combines intelligent document ingestion, vector search, web enrichment, and AI-powered summarization. The system features a modern FastAPI backend with a beautiful Streamlit frontend.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   External      │
│   Frontend      │◄──►│   Backend       │◄──►│   Services      │
│   (Port 8501)   │    │   (Port 8000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   AI Pipeline   │
                       │                 │
                       │ • Model Router  │
                       │ • Embeddings    │
                       │ • Vector DB     │
                       │ • Reranker      │
                       │ • Summarizer    │
                       │ • Web Search    │
                       └─────────────────┘
```

## 📁 Project Structure

```
Kurushetra_2.0_Team_NeuralHacks/
├── 📁 server_FastAPI/           # FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📁 api/v1/          # API endpoints
│   │   ├── 📁 config/          # Configuration & model routing
│   │   ├── 📁 controllers/     # User management
│   │   ├── 📁 middlewares/     # Auth & file upload
│   │   ├── 📁 models/          # Database models
│   │   ├── 📁 prompts/         # AI prompt templates
│   │   ├── 📁 services/        # Core AI services
│   │   └── 📁 utils/           # Utility functions
│   ├── 📁 docs/                # API documentation
│   ├── 📁 tests/               # Unit tests
│   └── 📄 main.py              # FastAPI application
├── 📁 streamlit_frontend/       # Streamlit Frontend
│   ├── 📄 app.py               # Main Streamlit application
│   ├── 📄 requirements.txt     # Python dependencies
│   ├── 📄 test_frontend.py    # Frontend tests
│   └── 📄 README.md            # Frontend documentation
├── 📁 client/                  # Next.js Frontend (legacy)
├── 📁 server/                  # Express.js Backend (legacy)
└── 📄 demo_full_stack.py       # Full stack demo script
```

## 🚀 Key Features

### 🔍 AI-Powered Search
- **Intelligent Model Routing**: Automatically selects the best AI model for each query type
- **Vector Search**: FAISS-based similarity search with embeddings
- **Reranking**: Cross-encoder models for improved result relevance
- **Web Enrichment**: Combines document results with web search results
- **AI Summarization**: Generates comprehensive answers with source citations

### 📤 Document Processing
- **Multi-format Support**: PDF, DOCX, TXT files
- **Automatic Chunking**: Intelligent text segmentation for optimal search
- **Vector Indexing**: Real-time embedding generation and storage
- **Background Processing**: Asynchronous file processing with Redis queues

### 🎨 Modern User Interface
- **Streamlit Frontend**: Beautiful, responsive web interface
- **Real-time Updates**: Live status monitoring and progress tracking
- **File Management**: Comprehensive document overview and content preview
- **Search Analytics**: Performance metrics and system health monitoring

## 🛠️ Technology Stack

### Backend (FastAPI)
- **Framework**: FastAPI with async/await support
- **AI/ML**: Ollama, Sentence Transformers, FAISS
- **Database**: MongoDB with Motor async driver
- **Queue System**: Redis + RQ for background tasks
- **Storage**: Local filesystem + S3 support
- **Authentication**: JWT-based security

### Frontend (Streamlit)
- **Framework**: Streamlit for rapid web app development
- **Styling**: Custom CSS with modern design principles
- **Data Display**: Pandas DataFrames and interactive charts
- **Real-time**: Live updates and progress indicators

### AI Pipeline
- **Model Router**: Intent classification and model selection
- **Embeddings**: Sentence Transformers for text vectorization
- **Vector DB**: FAISS for efficient similarity search
- **Reranking**: Cross-encoder models for result improvement
- **Summarization**: LLM-based answer generation
- **Web Search**: Content enrichment from web sources

## 🔧 Setup Instructions

### Prerequisites
1. **Python 3.8+**
2. **Redis Server** (for background tasks)
3. **Ollama** (for local LLM inference)
4. **MongoDB** (for user management)

### Quick Start

#### Option 1: Full Stack Demo
```bash
# Run the complete demo script
python demo_full_stack.py --demo
```

#### Option 2: Manual Setup
```bash
# 1. Start Backend
cd server_FastAPI
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# 2. Start Frontend (in new terminal)
cd streamlit_frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### Environment Configuration
```bash
# Backend (.env)
MONGODB_URL=mongodb://localhost:27017
ACCESS_TOKEN_SECRET=your_secret_key
OLLAMA_HOST=http://localhost:11434

# Frontend (.env)
API_BASE_URL=http://localhost:8000
API_TOKEN=your_jwt_token
```

## 📊 API Endpoints

### Core Endpoints
- `POST /api/v1/upload` - File upload and processing
- `POST /api/v1/search` - Intelligent search with AI pipeline
- `GET /api/v1/files` - List workspace documents
- `GET /api/v1/file/{id}` - Document information and content

### User Management
- `POST /api/register` - User registration
- `POST /api/login` - User authentication
- `GET /api/profile` - User profile information

### Health & Status
- `GET /health` - System health check
- `GET /` - API information and documentation links

## 🎯 Use Cases

### 1. Research & Analysis
- Upload research papers and documents
- Ask complex questions with natural language
- Get AI-generated summaries with source citations
- Enrich results with web search integration

### 2. Document Management
- Organize documents by workspace
- Track processing status and metadata
- Preview document content and chunks
- Monitor system performance

### 3. Knowledge Discovery
- Semantic search across document collections
- Find related content and connections
- Generate insights from multiple sources
- Maintain provenance and citations

## 🔒 Security Features

- **JWT Authentication**: Secure token-based access control
- **Workspace Isolation**: User data separation and privacy
- **File Validation**: Secure file upload and processing
- **API Rate Limiting**: Protection against abuse
- **Input Sanitization**: XSS and injection prevention

## 📈 Performance Features

- **Async Processing**: Non-blocking operations
- **Background Queues**: Efficient task management
- **Vector Caching**: Optimized similarity search
- **Lazy Loading**: On-demand content delivery
- **Connection Pooling**: Database and Redis optimization

## 🧪 Testing

### Backend Tests
```bash
cd server_FastAPI
pytest tests/ -v
```

### Frontend Tests
```bash
cd streamlit_frontend
python test_frontend.py
```

### Integration Tests
```bash
python demo_full_stack.py --demo
```

## 🚀 Deployment

### Development
- Local development with hot reload
- Environment-based configuration
- Debug mode and detailed logging

### Production
- Docker containerization support
- Environment variable management
- Health monitoring and metrics
- Load balancing ready

## 🔮 Future Enhancements

### Planned Features
- **Multi-modal Support**: Image and audio processing
- **Advanced Analytics**: Usage patterns and insights
- **Collaboration Tools**: Shared workspaces and permissions
- **API Marketplace**: Third-party integrations
- **Mobile App**: Native mobile experience

### Scalability Improvements
- **Microservices**: Service decomposition
- **Kubernetes**: Container orchestration
- **CDN Integration**: Global content delivery
- **Multi-tenant**: Enterprise features

## 🤝 Contributing

### Development Guidelines
1. **Code Style**: Follow PEP 8 and Streamlit best practices
2. **Testing**: Maintain test coverage above 80%
3. **Documentation**: Update docs for all changes
4. **Security**: Follow security best practices
5. **Performance**: Monitor and optimize critical paths

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📚 Documentation

### API Documentation
- **Swagger UI**: `/docs` endpoint
- **ReDoc**: `/redoc` endpoint
- **Markdown**: `docs/API_DOCS.md`

### User Guides
- **Frontend**: `streamlit_frontend/README.md`
- **Backend**: `server_FastAPI/README.md`
- **Quick Start**: This document

## 🆘 Support & Troubleshooting

### Common Issues
1. **Connection Errors**: Check Redis and MongoDB status
2. **Authentication**: Verify JWT token validity
3. **File Processing**: Check supported formats and size limits
4. **Performance**: Monitor system resources and queues

### Getting Help
- **Documentation**: Comprehensive guides and examples
- **Issues**: GitHub issue tracking
- **Community**: Developer discussions and support
- **Testing**: Automated test suites and validation

## 📄 License

This project is licensed under the same terms as the main OmniSearch AI project.

## 🎉 Conclusion

OmniSearch AI represents a complete, production-ready solution for intelligent document search and analysis. With its modern architecture, comprehensive feature set, and beautiful user interface, it provides a powerful platform for knowledge discovery and document management.

The system successfully combines cutting-edge AI technologies with practical usability, making advanced document search accessible to users of all technical levels. Whether you're a researcher, analyst, or knowledge worker, OmniSearch AI offers the tools you need to unlock insights from your document collections.

---

**Ready to get started? Run `python demo_full_stack.py --demo` and experience the power of AI-powered document search! 🚀**
