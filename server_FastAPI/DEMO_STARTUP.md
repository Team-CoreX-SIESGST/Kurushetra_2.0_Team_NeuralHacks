# 🚀 OmniSearch AI - Demo Startup Guide

## 🎯 **Quick Start (2 Methods)**

### **Method 1: Automatic Startup Script**
```bash
# Option A: Batch File (Recommended for Windows)
double-click start_demo.bat

# Option B: PowerShell Script  
powershell -ExecutionPolicy Bypass -File "start_demo.ps1"
```

### **Method 2: Manual Startup**
**Terminal 1 - FastAPI Server:**
```bash
cd "D:\Kurukshetra 25\Kurushetra_2.0_Team_NeuralHacks\server_FastAPI"
python run_server.py --safe-demo --port 8000
```

**Terminal 2 - Streamlit Frontend:**
```bash
cd "D:\Kurukshetra 25\Kurushetra_2.0_Team_NeuralHacks\streamlit_frontend"
streamlit run app.py --server.port 8501
```

---

## 📊 **Access Points**

| Service | URL | Description |
|---------|-----|-------------|
| **🔍 Streamlit Frontend** | http://localhost:8501 | Main user interface |
| **⚡ FastAPI Server** | http://localhost:8000 | Backend API server |
| **📖 API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **📚 Alternative Docs** | http://localhost:8000/redoc | ReDoc API documentation |

---

## 🛡️ **Active Safe Demo Protections**

✅ **Resource-Optimized Configuration:**
- **Memory**: Lightweight embedder (384D vectors)
- **Processing**: 16-item batches, single worker
- **Storage**: Disk-backed FAISS IVF index (nlist=100)
- **Limits**: 10MB max file size, conservative chunking
- **Guards**: Auto-detects low RAM systems

✅ **System Requirements Met:**
- **RAM**: 9.0GB available / 15.7GB total ✅
- **CPU**: 12 cores (8 physical) ✅ 
- **Storage**: 128GB free ✅
- **Dependencies**: All installed ✅
- **Redis**: Running ✅

---

## 🧪 **Demo Features**

### **📤 File Upload & Processing**
- Upload PDF, DOCX, TXT files
- Automatic chunking and vectorization
- Background processing with status tracking
- Source attribution and metadata extraction

### **🔍 Intelligent Search**
- Vector similarity search with FAISS
- Web search integration (optional)
- AI model routing (CodeLlama, Llama2, etc.)
- Cross-encoder reranking (disabled for safety)
- LLM summarization with citations

### **📁 File Management**
- Workspace-based file organization
- Processing status monitoring
- File metadata and content preview
- Vector database statistics

### **📊 Analytics Dashboard**
- Search performance metrics
- Resource usage monitoring
- System health indicators

---

## 🔧 **Command Line Options**

### **Server Options:**
```bash
python run_server.py --help

# Safety modes
--safe-demo              # Enable comprehensive safe mode
--skip-embeddings        # Ultra-safe (disable vector generation)
--skip-rerank           # Moderate RAM savings 
--skip-summarizer       # Moderate CPU savings
--no-models             # Ultra-lightweight mode

# Server config
--port 8000             # Custom port
--host 0.0.0.0          # Custom host
--no-reload             # Disable auto-reload
--log-level debug       # Logging level

# Diagnostics
--check-resources       # System resource check
--generate-env          # Generate optimized .env
```

### **Resource Diagnostics:**
```bash
# Full system analysis
python diagnose_resources.py

# Generate optimized configuration
python diagnose_resources.py --generate-env

# JSON output for automation
python diagnose_resources.py --json

# Memory estimation
python diagnose_resources.py --estimate-chunks 10000
```

---

## 🏃‍♂️ **Demo Workflow**

### **Step 1: Start Services**
1. Run diagnostic check: `python diagnose_resources.py`
2. Start FastAPI server: `python run_server.py --safe-demo`  
3. Start Streamlit frontend: `streamlit run ../streamlit_frontend/app.py`
4. Open browser to: http://localhost:8501

### **Step 2: Upload Documents**
1. Go to "📤 Upload Files" tab
2. Choose a test file (PDF/DOCX/TXT)
3. Click "🚀 Upload & Process"
4. Monitor processing in "📁 File Management" tab

### **Step 3: Search & Query**
1. Go to "🔍 Search" tab
2. Enter search query (e.g., "What are the key findings?")
3. Configure options (web search, reranking, etc.)
4. Click "🔍 Search" and view AI-generated results

### **Step 4: Explore Features**
- View file metadata and chunks
- Check system analytics
- Test different search configurations
- Monitor resource usage

---

## 🛠️ **Troubleshooting**

### **Common Issues:**

**❌ "Cannot connect to API server"**
- Ensure FastAPI server is running on port 8000
- Check Windows Firewall settings
- Verify no other services using port 8000

**❌ "Redis connection failed"**
- Start Redis server: `redis-server`
- Check Redis is running on default port 6379

**❌ "Module not found" errors**
- Install requirements: `pip install -r requirements.txt`
- Activate correct Python environment

**❌ "File upload fails"**
- Check file size < 10MB limit
- Verify supported format (PDF/DOCX/TXT)
- Ensure workspace has write permissions

### **Performance Optimization:**
```bash
# Check current resource usage
python diagnose_resources.py

# Generate optimal configuration  
python diagnose_resources.py --generate-env
cp .env.optimized .env

# Ultra-safe mode for low RAM
python run_server.py --no-models --skip-embeddings
```

---

## 📈 **Expected Performance**

**For Typical Demo Workload (10 documents, ~500KB each):**
- **Memory Usage**: ~470MB total
- **Processing Time**: ~2-3 minutes per document  
- **Vector Index**: 22MB for 10K chunks
- **Search Latency**: <500ms for similarity search

**Resource Usage:**
- **RAM**: ~1-2GB total (including Python overhead)
- **CPU**: Single-threaded processing to prevent thrashing
- **Storage**: ~100MB for indexes and metadata

---

## 🎉 **Success Indicators**

✅ **System Ready When:**
- FastAPI server shows: "Application startup complete"
- Streamlit displays: "You can now view your Streamlit app"
- Health check responds: `curl http://localhost:8000/health`
- No error messages in console logs
- Resource diagnostic shows: "SYSTEM READY"

✅ **Demo Working When:**
- File upload succeeds with status tracking
- Search returns relevant results with sources
- AI generates coherent summaries
- Response times < 5 seconds
- No memory/CPU warnings in logs

---

## 🏆 **Next Steps**

After successful demo, consider:
- **Production Deployment**: Use `--no-reload` and process manager
- **Scaling**: Enable `ENABLE_RERANK=true` on powerful systems
- **Integration**: Connect to external LLM APIs for better responses
- **Monitoring**: Set up logging and metrics collection
- **Security**: Add proper authentication beyond demo mode

---

**🎯 Your OmniSearch AI safe demo environment is ready!**
**Open http://localhost:8501 and start exploring! 🚀**
