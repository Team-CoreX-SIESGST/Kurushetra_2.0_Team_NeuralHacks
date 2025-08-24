#!/usr/bin/env python3
"""
OmniSearch AI - Full Stack Demo Script

This script demonstrates how to run both the FastAPI backend and Streamlit frontend
for the complete OmniSearch AI application.

Prerequisites:
- Python 3.8+
- Redis server running (optional for demo)
- Ollama installed and running
- Required Python packages installed

Usage:
    python demo_full_stack.py [--backend-only] [--frontend-only] [--help]
"""

import argparse
import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def check_prerequisites():
    """Check if all required services are available."""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check if required packages are installed
    try:
        import fastapi
        import streamlit
        import redis
        print("✅ Python packages: OK")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False
    
    # Check Redis connection (optional for demo)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis: OK")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   Redis is optional for demo - continuing without it")
        print("   For full functionality, please install and start Redis")
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama: OK")
        else:
            print("❌ Ollama not responding properly")
            return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("   Please ensure Ollama is running on localhost:11434")
        return False
    
    print("✅ All prerequisites met!")
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("\n🚀 Starting FastAPI Backend...")
    
    # Get the original working directory
    original_dir = os.getcwd()
    backend_dir = Path(original_dir) / "server_FastAPI"
    
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        return None
    
    # Check if .env exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found. Creating example...")
        example_env = backend_dir / "example_env.txt"
        if example_env.exists():
            with open(example_env, "r") as f:
                env_content = f.read()
            with open(env_file, "w") as f:
                f.write(env_content)
            print("✅ Created .env from example_env.txt")
    
    # Start the backend
    try:
        print("Starting FastAPI server on http://localhost:8000")
        print("API Documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the backend")
        
        # Start uvicorn server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], cwd=str(backend_dir))
        
        return process
    
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend."""
    print("\n🎨 Starting Streamlit Frontend...")
    
    # Get the original working directory
    original_dir = os.getcwd()
    frontend_dir = Path(original_dir) / "streamlit_frontend"
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return None
    
    # Check if requirements are installed
    try:
        import streamlit
        print("✅ Streamlit already installed")
    except ImportError:
        print("📦 Installing Streamlit requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(frontend_dir / "requirements.txt")])
    
    # Start Streamlit
    try:
        print("Starting Streamlit frontend on http://localhost:8501")
        print("Press Ctrl+C to stop the frontend")
        
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", str(frontend_dir / "app.py"),
            "--server.port", "8501",
            "--server.headless", "true"
        ])
        
        return process
    
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def wait_for_backend():
    """Wait for the backend to be ready."""
    print("⏳ Waiting for backend to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
            time.sleep(2)
    
    print("❌ Backend failed to start within expected time")
    return False

def run_demo():
    """Run a quick demo of the system."""
    print("\n🎯 Running Quick Demo...")
    
    # Wait for backend
    if not wait_for_backend():
        return
    
    # Test basic endpoints
    try:
        # Health check
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health check: {response.status_code}")
        
        # Root endpoint
        response = requests.get("http://localhost:8000/")
        print(f"✅ Root endpoint: {response.status_code}")
        
        # API docs
        response = requests.get("http://localhost:8000/docs")
        print(f"✅ API docs: {response.status_code}")
        
        print("\n🎉 Demo completed successfully!")
        print("\n📚 Next Steps:")
        print("1. Open http://localhost:8501 in your browser for the frontend")
        print("2. Open http://localhost:8000/docs for API documentation")
        print("3. Try uploading a document and searching!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="OmniSearch AI Full Stack Demo")
    parser.add_argument("--backend-only", action="store_true", help="Start only the backend")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the frontend")
    parser.add_argument("--demo", action="store_true", help="Run a quick demo after starting services")
    
    args = parser.parse_args()
    
    print("🔍 OmniSearch AI - Full Stack Demo")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    processes = []
    
    try:
        if not args.frontend_only:
            # Start backend
            backend_process = start_backend()
            if backend_process:
                processes.append(("Backend", backend_process))
                time.sleep(3)  # Give backend time to start
        
        if not args.backend_only:
            # Start frontend
            frontend_process = start_frontend()
            if frontend_process:
                processes.append(("Frontend", frontend_process))
        
        # Run demo if requested
        if args.demo and not args.frontend_only:
            time.sleep(5)  # Wait for services to start
            run_demo()
        
        # Keep running until interrupted
        if processes:
            print(f"\n🚀 Services started successfully!")
            print("Press Ctrl+C to stop all services")
            
            try:
                # Wait for processes
                for name, process in processes:
                    process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down services...")
                
                for name, process in processes:
                    print(f"   Stopping {name}...")
                    process.terminate()
                    process.wait()
                
                print("✅ All services stopped")
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Clean up processes
        for name, process in processes:
            try:
                process.terminate()
                process.wait()
            except:
                pass

if __name__ == "__main__":
    main()
