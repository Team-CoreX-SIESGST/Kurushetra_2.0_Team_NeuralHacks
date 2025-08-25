#!/usr/bin/env python3
"""
OmniSearch AI Environment Setup Script
Automatically installs dependencies and sets up the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} failed with error: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   Please use Python 3.8 or higher")
        return False

def install_requirements(env_type="dev"):
    """Install requirements based on environment type"""
    requirements_files = {
        "dev": "requirements-dev.txt",
        "prod": "requirements-prod.txt",
        "minimal": "requirements.txt"
    }
    
    req_file = requirements_files.get(env_type, "requirements.txt")
    
    if not Path(req_file).exists():
        print(f"❌ Requirements file {req_file} not found")
        return False
    
    print(f"📦 Installing {env_type} requirements from {req_file}...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r {req_file}", f"Installing {env_type} requirements"):
        return False
    
    return True

def create_env_file():
    """Create .env file from example if it doesn't exist"""
    env_file = Path(".env")
    example_file = Path("example_env.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if example_file.exists():
        print("📝 Creating .env file from example...")
        try:
            env_file.write_text(example_file.read_text())
            print("✅ .env file created successfully")
            print("⚠️  Please edit .env file with your configuration")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  example_env.txt not found, creating basic .env file...")
        basic_env = """# OmniSearch AI Configuration
MONGODB_URL=mongodb://localhost:27017/omnisearch
SERVER_PORT=8000
ACCESS_TOKEN_SECRET=your_secret_key_change_this
REFRESH_TOKEN_SECRET=your_refresh_secret_change_this

# Optional: Gemini AI (for enhanced features)
# GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Cloudinary (for file storage)
# CLOUDINARY_CLOUD_NAME=your_cloud_name
# CLOUDINARY_API_KEY=your_api_key
# CLOUDINARY_API_SECRET=your_api_secret
"""
        try:
            env_file.write_text(basic_env)
            print("✅ Basic .env file created")
            print("⚠️  Please edit .env file with your configuration")
            return True
        except Exception as e:
            print(f"❌ Failed to create basic .env file: {e}")
            return False

def verify_installation():
    """Verify that critical packages are installed"""
    print("🔍 Verifying installation...")
    
    critical_packages = [
        "fastapi",
        "uvicorn",
        "pydantic", 
        "motor",
        "google.generativeai"
    ]
    
    all_good = True
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed correctly")
        except ImportError:
            print(f"❌ {package} not found")
            all_good = False
    
    return all_good

def main():
    """Main setup function"""
    print("🚀 OmniSearch AI Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Ask for environment type
    print("\n📋 Select installation type:")
    print("1. Development (includes testing and dev tools)")
    print("2. Production (minimal dependencies)")
    print("3. Basic (core dependencies only)")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    env_types = {"1": "dev", "2": "prod", "3": "minimal"}
    env_type = env_types[choice]
    
    # Install requirements
    if not install_requirements(env_type):
        print("❌ Installation failed")
        return False
    
    # Create .env file
    if not create_env_file():
        print("⚠️  .env file creation failed, but continuing...")
    
    # Verify installation
    if not verify_installation():
        print("⚠️  Some packages may not be installed correctly")
        print("   Try running: pip install -r requirements.txt")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    
    print("\n📋 Next steps:")
    print("1. Edit the .env file with your configuration")
    print("2. Start the server: python run_server.py")
    print("3. Visit: http://localhost:8000/docs")
    
    if env_type == "dev":
        print("\n🛠️  Development tools available:")
        print("- Code formatting: black .")
        print("- Linting: flake8 app/")
        print("- Testing: pytest tests/")
        print("- Type checking: mypy app/")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
