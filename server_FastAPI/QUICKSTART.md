# OmniSearch AI - Quick Start Guide

🚀 **Get your AI-powered search system running in minutes!**

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Quick Setup (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python run_server.py
```

The script will:
- ✅ Check all requirements
- ✅ Verify environment configuration
- ✅ Start the server on http://localhost:8000

### 3. Test the System
```bash
python demo_test_script.py
```

This will run comprehensive tests of all endpoints and functionality.

## What's Included

### 🎭 Demo Mode
- **Authentication bypassed** for easy testing
- **Sample data** already provided
- **No external dependencies** required initially

### 📚 Sample Documents
Pre-loaded demo workspace with:
- AI Research Overview
- Machine Learning Fundamentals  
- Deep Learning Guide

### 🔍 Search Capabilities
- **Vector search** with FAISS
- **AI-powered summarization**
- **Intent classification**
- **Source citation**

## API Endpoints

Once running, visit these URLs:

- 🏠 **Main API**: http://localhost:8000
- 📖 **Documentation**: http://localhost:8000/docs
- 📋 **Alternative Docs**: http://localhost:8000/redoc
- ❤️ **Health Check**: http://localhost:8000/health

## Key Features Working Out-of-the-Box

### ✅ File Upload & Processing
- Upload PDF, DOCX, TXT files
- Automatic text extraction
- Vector embedding generation
- Workspace organization

### ✅ AI Search Pipeline
- Intelligent query understanding
- Vector similarity search
- Result ranking and filtering
- AI-powered summarization

### ✅ Multiple Search Types
- **Simple Search**: Fast vector search
- **Full Search**: Complete AI pipeline with summarization
- **Stats**: Workspace analytics

## Sample API Calls

### Upload a File
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "workspace_id=demo-workspace" \
  -F "file=@your_document.pdf"
```

### Search Documents  
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "demo-workspace",
    "query": "key findings of AI research",
    "top_k": 5,
    "summarize": true
  }'
```

### List Files
```bash
curl "http://localhost:8000/api/v1/files?workspace_id=demo-workspace"
```

## Troubleshooting

### Common Issues

**❌ Server won't start**
- Check if port 8000 is available
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**❌ No search results**  
- Verify demo files exist in `demo-workspace/` folder
- Check if embeddings are being generated (watch server logs)

**❌ Import errors**
- Install missing packages: `pip install sentence-transformers faiss-cpu`
- Use Python 3.8+ version

## Advanced Configuration

### Environment Variables (.env file)
```bash
# Demo mode (bypasses authentication)
DEMO_MODE=true

# Server settings
SERVER_PORT=8000

# Vector database
VECTOR_DB_TYPE=faiss

# Ollama (optional for advanced features)
OLLAMA_HOST=http://localhost:11434
```

### Production Setup
For production use:
1. Set `DEMO_MODE=false`
2. Configure MongoDB URL
3. Set up proper authentication secrets
4. Configure cloud storage (optional)

## Next Steps

1. **Try the demo**: Run `python demo_test_script.py`
2. **Upload your files**: Use the `/api/v1/upload` endpoint
3. **Explore the docs**: Visit http://localhost:8000/docs
4. **Customize settings**: Edit the `.env` file
5. **Add more models**: Configure Ollama for advanced AI features

## Support

- 📖 **Full Documentation**: See `README.md`
- 🐛 **Issues**: Check server logs for errors
- 💡 **Features**: All endpoints documented at `/docs`

---

**🎉 You're ready to go! The AI search system is now running with demo data.**

**Next Command**: `python demo_test_script.py` to see it in action!
