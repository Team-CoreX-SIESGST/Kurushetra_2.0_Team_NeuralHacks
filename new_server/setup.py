#!/usr/bin/env python3
"""
Setup script for File Processing & RAG System
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version} is compatible")

def create_virtual_environment():
    """Create a virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        sys.exit(1)

def get_venv_python():
    """Get the path to the Python executable in the virtual environment"""
    if os.name == 'nt':  # Windows
        return Path("venv/Scripts/python.exe")
    else:  # Linux/Mac
        return Path("venv/bin/python")

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    python_path = get_venv_python()
    
    try:
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(python_path), "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ All packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        sys.exit(1)

def setup_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "extracted_data", 
        "processed_data",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Setup environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file and add your Gemini API key")
    else:
        print("ℹ️  .env file already exists or .env.example not found")

def check_tesseract():
    """Check if Tesseract is installed (for OCR functionality)"""
    try:
        subprocess.run(["tesseract", "--version"], 
                      capture_output=True, check=True)
        print("✅ Tesseract OCR is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Tesseract OCR not found. OCR functionality will not work.")
        print("   Install from: https://github.com/tesseract-ocr/tesseract")

def print_usage():
    """Print usage instructions"""
    python_path = get_venv_python()
    
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Edit the .env file and add your Gemini API key:")
    print("   GEMINI_API_KEY=your_actual_api_key_here")
    print("\n2. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("   source venv/bin/activate")
    
    print("\n3. Start the server:")
    print(f"   {python_path} main.py")
    print("   OR")
    print(f"   {python_path} -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    
    print("\n4. Open your browser and go to:")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs (API documentation)")
    
    print("\n📚 Supported file formats:")
    formats = [
        "PDF (.pdf)", "Word (.docx, .doc)", "Excel (.xlsx, .xls)",
        "PowerPoint (.pptx, .ppt)", "CSV (.csv)", "Text (.txt)",
        "JSON (.json)", "XML (.xml)", "HTML (.html, .htm)",
        "Markdown (.md)", "Images (.png, .jpg, .jpeg, .tiff)"
    ]
    for fmt in formats:
        print(f"   • {fmt}")
    
    print("\n🔧 API Endpoints:")
    endpoints = [
        "GET  /supported-formats - List supported file formats",
        "POST /process-file - Extract data from file to JSON",
        "POST /process-and-summarize - Process file and generate AI summary",
        "POST /summarize-json - Generate summary from JSON data",
        "GET  /health - Check system health"
    ]
    for endpoint in endpoints:
        print(f"   • {endpoint}")

def main():
    """Main setup function"""
    print("🚀 File Processing & RAG System Setup")
    print("="*50)
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install requirements
    install_requirements()
    
    # Setup directories
    setup_directories()
    
    # Setup environment
    setup_environment()
    
    # Check optional dependencies
    check_tesseract()
    
    # Print usage instructions
    print_usage()

if __name__ == "__main__":
    main()
