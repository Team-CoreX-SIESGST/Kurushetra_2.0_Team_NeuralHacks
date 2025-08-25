#!/usr/bin/env python3
"""
Comprehensive diagnostic and fix script for the File Processing & RAG System
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import importlib.util

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)

def print_step(step, message):
    """Print a formatted step"""
    print(f"\n{step}. {message}")

def check_python():
    """Check Python installation and version"""
    print_header("PYTHON INSTALLATION CHECK")
    
    try:
        version = sys.version_info
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ required!")
            print("🔗 Download from: https://python.org")
            return False
        
        # Check pip
        try:
            import pip
            print("✅ pip is available")
        except ImportError:
            print("⚠️ pip not found, trying to install...")
            try:
                subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
                print("✅ pip installed successfully")
            except:
                print("❌ Failed to install pip")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False

def check_directory_structure():
    """Check if all required files exist"""
    print_header("DIRECTORY STRUCTURE CHECK")
    
    required_files = [
        "main.py",
        "file_processor.py", 
        "rag_system.py",
        "streamlit_app.py",
        "requirements.txt",
        ".env.example"
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        print("💡 Make sure you're in the correct directory:")
        print("   cd \"C:\\Users\\paras\\OneDrive\\Documents\\Desktop\\Kurushetra_2.0_Team_NeuralHacks\\new_server\"")
        return False
    
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    print_header("DEPENDENCIES CHECK")
    
    required_packages = {
        "fastapi": "FastAPI framework",
        "uvicorn": "ASGI server",
        "streamlit": "Frontend framework",
        "requests": "HTTP client",
        "aiohttp": "Async HTTP client",
        "python-dotenv": "Environment variables"
    }
    
    optional_packages = {
        "pandas": "Data processing",
        "PyPDF2": "PDF processing", 
        "python-docx": "Word documents",
        "openpyxl": "Excel files",
        "beautifulsoup4": "HTML parsing",
        "Pillow": "Image processing"
    }
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    for package, description in required_packages.items():
        try:
            importlib.import_module(package.replace("-", "_"))
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (REQUIRED)")
            missing_required.append(package)
    
    # Check optional packages
    for package, description in optional_packages.items():
        try:
            importlib.import_module(package.replace("-", "_"))
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"⚠️ {package} - {description} (optional)")
            missing_optional.append(package)
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        return False, missing_required
    
    if missing_optional:
        print(f"\n⚠️ Missing optional packages: {', '.join(missing_optional)}")
        print("💡 Some file formats may not be supported")
    
    return True, []

def install_dependencies():
    """Install missing dependencies"""
    print_header("INSTALLING DEPENDENCIES")
    
    print_step(1, "Upgrading pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True, text=True)
        print("✅ pip upgraded successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ pip upgrade warning: {e}")
    
    print_step(2, "Installing from requirements.txt...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              check=True, capture_output=True, text=True)
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e.stderr}")
        
        # Try installing core packages individually
        print_step(3, "Installing core packages individually...")
        core_packages = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0", 
            "streamlit==1.29.0",
            "requests==2.31.0",
            "python-dotenv==1.0.0",
            "pandas==2.1.4"
        ]
        
        for package in core_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True, text=True)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
        
        return False

def check_environment_file():
    """Check and fix environment file"""
    print_header("ENVIRONMENT FILE CHECK")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    # Check if .env exists
    if not env_file.exists():
        print("❌ .env file not found")
        
        if env_example.exists():
            print_step(1, "Creating .env from .env.example...")
            shutil.copy(env_example, env_file)
            print("✅ .env file created")
        else:
            print_step(1, "Creating default .env file...")
            with open(env_file, 'w') as f:
                f.write("# Gemini API Configuration\n")
                f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
                f.write("\n# Server Configuration\n")
                f.write("HOST=0.0.0.0\n")
                f.write("PORT=8000\n")
                f.write("DEBUG=True\n")
            print("✅ Default .env file created")
    
    # Check .env content
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "GEMINI_API_KEY=your_gemini_api_key_here" in content:
            print("⚠️ .env file still has placeholder API key")
            print("💡 Edit .env file and add your actual Gemini API key")
            print("🔗 Get API key from: https://makersuite.google.com/")
            return False
        elif "GEMINI_API_KEY=" in content:
            print("✅ .env file has API key configured")
            return True
        else:
            print("❌ .env file missing GEMINI_API_KEY")
            return False
            
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def check_ports():
    """Check if required ports are available"""
    print_header("PORT AVAILABILITY CHECK")
    
    import socket
    
    ports_to_check = [8000, 8501]
    
    for port in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                print(f"✅ Port {port} is available")
        except OSError:
            print(f"⚠️ Port {port} is already in use")
            print(f"💡 You can use different ports when starting the services")

def create_missing_directories():
    """Create required directories"""
    print_header("CREATING DIRECTORIES")
    
    directories = [
        "uploads",
        "extracted_data",
        "processed_data", 
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")

def test_imports():
    """Test importing main modules"""
    print_header("MODULE IMPORT TEST")
    
    modules_to_test = [
        ("file_processor", "FileProcessor"),
        ("rag_system", "RAGSystem"),
        ("main", "FastAPI app"),
        ("streamlit_app", "Streamlit frontend")
    ]
    
    for module_name, description in modules_to_test:
        try:
            if Path(f"{module_name}.py").exists():
                spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ {module_name}.py - {description}")
            else:
                print(f"❌ {module_name}.py - File not found")
        except Exception as e:
            print(f"❌ {module_name}.py - Import error: {e}")

def fix_common_issues():
    """Apply common fixes"""
    print_header("APPLYING COMMON FIXES")
    
    # Fix 1: Update requirements.txt if it has issues
    print_step(1, "Checking requirements.txt format...")
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        # Remove any problematic lines
        lines = [line.strip() for line in content.split('\n') 
                if line.strip() and not line.startswith('#')]
        
        # Ensure basic packages are present
        required_basic = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0", 
            "streamlit>=1.29.0",
            "requests>=2.31.0",
            "python-dotenv>=1.0.0"
        ]
        
        for req in required_basic:
            package_name = req.split('>=')[0].split('==')[0]
            if not any(package_name in line for line in lines):
                lines.append(req)
        
        with open("requirements.txt", "w") as f:
            f.write('\n'.join(lines))
        
        print("✅ requirements.txt validated")
        
    except Exception as e:
        print(f"❌ Error fixing requirements.txt: {e}")
    
    # Fix 2: Ensure proper file encoding
    print_step(2, "Checking file encodings...")
    try:
        python_files = ["main.py", "file_processor.py", "rag_system.py", "streamlit_app.py"]
        for file in python_files:
            if Path(file).exists():
                # Test if file can be read properly
                with open(file, 'r', encoding='utf-8') as f:
                    f.read()
                print(f"✅ {file} encoding OK")
    except Exception as e:
        print(f"⚠️ File encoding issue: {e}")

def generate_startup_script():
    """Generate a simple startup script"""
    print_header("GENERATING STARTUP SCRIPT")
    
    startup_script = '''@echo off
echo Starting File Processing & RAG System...
echo.

echo Checking Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Starting FastAPI backend...
start "FastAPI Backend" cmd /k "python main.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo Starting Streamlit frontend...
start "Streamlit Frontend" cmd /k "streamlit run streamlit_app.py"

echo.
echo ===================================
echo System started successfully!
echo ===================================
echo FastAPI Backend:  http://localhost:8000
echo Streamlit Frontend: http://localhost:8501
echo API Documentation: http://localhost:8000/docs
echo ===================================
echo.
echo Press any key to exit this window...
pause > nul
'''
    
    with open("start_system.bat", "w") as f:
        f.write(startup_script)
    
    print("✅ Created start_system.bat")
    print("💡 You can double-click start_system.bat to run the system")

def main():
    """Main diagnostic and fix function"""
    print("🚀 File Processing & RAG System - Issue Fixer")
    print("=" * 60)
    
    issues_found = []
    
    # Check Python
    if not check_python():
        issues_found.append("Python installation")
    
    # Check directory structure
    if not check_directory_structure():
        issues_found.append("Missing files")
        return
    
    # Check dependencies
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        print_step("FIX", "Installing missing dependencies...")
        if install_dependencies():
            print("✅ Dependencies fixed")
        else:
            issues_found.append("Dependencies installation")
    
    # Check environment file
    if not check_environment_file():
        issues_found.append("Environment configuration")
    
    # Check ports
    check_ports()
    
    # Create directories
    create_missing_directories()
    
    # Test imports
    test_imports()
    
    # Apply fixes
    fix_common_issues()
    
    # Generate startup script
    generate_startup_script()
    
    # Final report
    print_header("FINAL REPORT")
    
    if issues_found:
        print("⚠️ Issues that need manual attention:")
        for issue in issues_found:
            print(f"   • {issue}")
        
        print("\n💡 Next steps:")
        if "Environment configuration" in issues_found:
            print("   1. Edit .env file and add your Gemini API key")
            print("   2. Get API key from: https://makersuite.google.com/")
        if "Dependencies installation" in issues_found:
            print("   3. Try: pip install fastapi uvicorn streamlit requests python-dotenv")
        
        print("   4. Run: python main.py")
        print("   5. In another terminal: streamlit run streamlit_app.py")
    else:
        print("🎉 All checks passed! System should be ready to run.")
        print("\n🚀 To start the system:")
        print("   Option 1: Double-click start_system.bat")
        print("   Option 2: Run: python run_system.py") 
        print("   Option 3: Run manually:")
        print("      Terminal 1: python main.py")
        print("      Terminal 2: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
