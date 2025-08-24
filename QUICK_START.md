# 🚀 OmniSearch AI - Quick Start Guide

Get up and running with OmniSearch AI in under 5 minutes!

## ⚡ Super Quick Start

```bash
# 1. Clone and navigate to project
cd Kurushetra_2.0_Team_NeuralHacks

# 2. Run the full stack demo
python demo_full_stack.py --demo
```

That's it! The script will:
- ✅ Check all prerequisites
- 🚀 Start the FastAPI backend
- 🎨 Start the Streamlit frontend
- 🧪 Run a quick demo
- 🌐 Open both services in your browser

## 🔧 Manual Setup (Step by Step)

### Prerequisites Check
```bash
# Ensure you have:
# - Python 3.8+
# - Redis running on localhost:6379
# - Ollama running on localhost:11434
# - MongoDB running on localhost:27017
```

### 1. Start Backend
```bash
cd server_FastAPI

# Install dependencies
pip install -r requirements.txt

# Create .env from example
cp example_env.txt .env

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend (New Terminal)
```bash
cd streamlit_frontend

# Install dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run app.py --server.port 8501
```

### 3. Access Your Application
- 🌐 **Frontend**: http://localhost:8501
- 📚 **API Docs**: http://localhost:8000/docs
- 🏥 **Health Check**: http://localhost:8000/health

## 🎯 First Steps

### 1. Upload a Document
- Go to the **📤 Upload Files** tab
- Drag & drop a PDF, DOCX, or TXT file
- Watch the processing status

### 2. Search Your Documents
- Go to the **🔍 Search** tab
- Type a natural language query
- Get AI-powered answers with sources

### 3. Manage Files
- Go to the **📁 File Management** tab
- View all uploaded documents
- Check processing status and metadata

## 🔑 Configuration

### Environment Variables
```bash
# Backend (.env)
MONGODB_URL=mongodb://localhost:27017
ACCESS_TOKEN_SECRET=your_secret_key
OLLAMA_HOST=http://localhost:11434

# Frontend (.env)
API_BASE_URL=http://localhost:8000
API_TOKEN=your_jwt_token
```

### API Authentication
1. Register a user: `POST /api/register`
2. Login: `POST /api/login`
3. Use the returned JWT token in frontend

## 🐛 Troubleshooting

### Common Issues

**❌ "Cannot connect to API server"**
- Check if backend is running on port 8000
- Verify API_BASE_URL in frontend

**❌ "Redis connection failed"**
- Start Redis: `redis-server`
- Check Redis is running on localhost:6379

**❌ "Ollama connection failed"**
- Install Ollama: https://ollama.ai/
- Start Ollama service
- Check Ollama is running on localhost:11434

**❌ "MongoDB connection failed"**
- Install MongoDB
- Start MongoDB service
- Check MongoDB is running on localhost:27017

### Quick Fixes
```bash
# Check service status
redis-cli ping
curl http://localhost:11434/api/tags
mongosh --eval "db.runCommand('ping')"

# Restart services
sudo systemctl restart redis
sudo systemctl restart mongod
ollama serve
```

## 📊 System Requirements

### Minimum
- **RAM**: 4GB
- **Storage**: 2GB free space
- **CPU**: 2 cores

### Recommended
- **RAM**: 8GB+
- **Storage**: 10GB+ free space
- **CPU**: 4+ cores
- **GPU**: CUDA-compatible (optional, for faster AI)

## 🎉 Success Indicators

You'll know everything is working when you see:
- ✅ Backend health check returns 200
- ✅ Frontend loads without errors
- ✅ File upload completes successfully
- ✅ Search returns AI-generated answers
- ✅ File management shows uploaded documents

## 🚀 Next Steps

1. **Explore Features**: Try different search options and file types
2. **Customize**: Modify prompts and model configurations
3. **Scale Up**: Add more documents and test performance
4. **Integrate**: Connect with your existing systems
5. **Deploy**: Move to production environment

## 📚 Need Help?

- 📖 **Full Documentation**: `PROJECT_OVERVIEW.md`
- 🧪 **Run Tests**: `python demo_full_stack.py --demo`
- 🐛 **Check Logs**: Backend and frontend console output
- 💬 **Community**: GitHub issues and discussions

---

**🎯 Ready to revolutionize your document search? Start with `python demo_full_stack.py --demo` and experience the power of AI-powered knowledge discovery!**
