#!/usr/bin/env python3
"""
Validate OmniSearch AI Requirements
Checks which packages are installed and which are missing
"""

import importlib
import sys
from pathlib import Path

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    test_name = import_name or package_name
    try:
        importlib.import_module(test_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def main():
    """Main validation function"""
    print("🔍 OmniSearch AI Requirements Validation")
    print("=" * 50)
    
    # Critical packages for basic functionality
    critical_packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("python-multipart", "multipart"),
        ("requests", "requests"),
        ("aiohttp", "aiohttp"),
        ("beautifulsoup4", "bs4"),
        ("motor", "motor"),
        ("pymongo", "pymongo"),
        ("redis", "redis"),
        ("python-dotenv", "dotenv"),
        ("google-generativeai", "google.generativeai"),
    ]
    
    # Document processing packages
    document_packages = [
        ("PyPDF2", "PyPDF2"),
        ("python-docx", "docx"),
        ("striprtf", "striprtf.striprtf"),
        ("odfpy", "odf"),
        ("markdown", "markdown"),
        ("pandas", "pandas"),
    ]
    
    # System packages
    system_packages = [
        ("psutil", "psutil"),
        ("numpy", "numpy"),
        ("chardet", "chardet"),
        ("httpx", "httpx"),
    ]
    
    # Security packages
    security_packages = [
        ("bcrypt", "bcrypt"),
        ("PyJWT", "jwt"),
        ("python-jose", "jose"),
        ("passlib", "passlib"),
    ]
    
    all_packages = [
        ("🔧 Core Framework", critical_packages),
        ("📄 Document Processing", document_packages),
        ("💾 System & Utilities", system_packages),
        ("🔒 Security & Auth", security_packages),
    ]
    
    total_packages = 0
    installed_packages = 0
    missing_packages = []
    
    for category, packages in all_packages:
        print(f"\n{category}")
        print("-" * 30)
        
        for package_name, import_name in packages:
            total_packages += 1
            is_installed, error = check_package(package_name, import_name)
            
            if is_installed:
                print(f"✅ {package_name}")
                installed_packages += 1
            else:
                print(f"❌ {package_name} - {error}")
                missing_packages.append(package_name)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    print(f"Total packages checked: {total_packages}")
    print(f"Installed: {installed_packages} ✅")
    print(f"Missing: {len(missing_packages)} ❌")
    print(f"Success rate: {(installed_packages/total_packages)*100:.1f}%")
    
    if missing_packages:
        print(f"\n❌ Missing packages:")
        for package in missing_packages:
            print(f"   • {package}")
        
        print(f"\n🔧 To install missing packages:")
        print("   pip install -r requirements.txt")
        print("   or")
        print("   python setup_environment.py")
        
        # Check if requirements files exist
        req_files = ["requirements.txt", "requirements-dev.txt", "requirements-prod.txt"]
        print(f"\n📋 Available requirements files:")
        for req_file in req_files:
            if Path(req_file).exists():
                print(f"   ✅ {req_file}")
            else:
                print(f"   ❌ {req_file}")
    else:
        print("\n🎉 All packages are installed correctly!")
        print("✅ Your environment is ready for OmniSearch AI")
    
    # Environment check
    print(f"\n🐍 Python version: {sys.version}")
    print(f"📁 Current directory: {Path.cwd()}")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found - you may need to create one")
    
    return len(missing_packages) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
