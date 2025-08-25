#!/usr/bin/env python3
"""
Simple script to run both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_python():
    """Check if Python is available"""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Using Python: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Python not found: {e}")
        return False

def check_requirements():
    """Check if requirements are installed"""
    required_packages = ["fastapi", "streamlit", "uvicorn"]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            print("Run: pip install -r requirements.txt")
            return False
    
    return True

def start_backend():
    """Start FastAPI backend"""
    print("\n🚀 Starting FastAPI backend...")
    try:
        # Start uvicorn server
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
        print("✅ FastAPI backend started on http://localhost:8000")
        return backend_process
    
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start Streamlit frontend"""
    print("\n🎨 Starting Streamlit frontend...")
    time.sleep(3)  # Give backend time to start
    
    try:
        # Start streamlit
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", 
            "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
        
        print("✅ Streamlit frontend started on http://localhost:8501")
        return frontend_process
    
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main function to run the system"""
    print("🚀 File Processing & RAG System Launcher")
    print("=" * 50)
    
    # Check Python
    if not check_python():
        return
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check if .env exists
    if not Path(".env").exists():
        print("\n⚠️  .env file not found!")
        print("1. Copy .env.example to .env")
        print("2. Add your Gemini API key")
        print("3. Run this script again")
        return
    
    print("\n📋 Starting services...")
    
    # Start backend
    backend = start_backend()
    if not backend:
        return
    
    # Start frontend
    frontend = start_frontend()
    if not frontend:
        backend.terminate()
        return
    
    print("\n" + "=" * 60)
    print("🎉 SYSTEM STARTED SUCCESSFULLY!")
    print("=" * 60)
    print("📊 FastAPI Backend:  http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🎨 Streamlit Frontend: http://localhost:8501")
    print("=" * 60)
    print("\n💡 Usage:")
    print("1. Open http://localhost:8501 in your browser")
    print("2. Upload files and get AI summaries")
    print("3. Press Ctrl+C to stop both services")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down services...")
        
        if backend:
            backend.terminate()
            backend.wait()
            print("✅ FastAPI backend stopped")
        
        if frontend:
            frontend.terminate() 
            frontend.wait()
            print("✅ Streamlit frontend stopped")
        
        print("👋 System shut down successfully!")

if __name__ == "__main__":
    main()
