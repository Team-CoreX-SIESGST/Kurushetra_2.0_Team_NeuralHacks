#!/usr/bin/env python3
"""
Quick installation script for core dependencies
"""

import subprocess
import sys

def install_core_packages():
    """Install core packages one by one"""
    print("🚀 Quick Installation of Core Packages")
    print("=" * 50)
    
    # Core packages in order of importance
    packages = [
        ("python-dotenv", "Environment variables"),
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("streamlit", "Frontend framework"),
        ("requests", "HTTP client"),
        ("aiohttp", "Async HTTP client"),
        ("pandas", "Data processing"),
        ("PyPDF2", "PDF processing"),
        ("python-docx", "Word documents"),
        ("openpyxl", "Excel files"),
        ("beautifulsoup4", "HTML parsing"),
        ("lxml", "XML processing"),
        ("Pillow", "Image processing"),
        ("markdown", "Markdown processing")
    ]
    
    installed = []
    failed = []
    
    for package, description in packages:
        print(f"\n📦 Installing {package} ({description})...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", package, "--upgrade"
            ], check=True, capture_output=True, text=True)
            print(f"✅ {package} installed successfully")
            installed.append(package)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}")
            failed.append(package)
    
    print("\n" + "=" * 50)
    print("📊 INSTALLATION SUMMARY")
    print("=" * 50)
    print(f"✅ Successfully installed: {len(installed)} packages")
    for pkg in installed:
        print(f"   • {pkg}")
    
    if failed:
        print(f"\n❌ Failed to install: {len(failed)} packages")
        for pkg in failed:
            print(f"   • {pkg}")
        
        print("\n💡 Try installing failed packages manually:")
        for pkg in failed:
            print(f"   pip install {pkg}")
    
    return len(failed) == 0

if __name__ == "__main__":
    success = install_core_packages()
    
    if success:
        print("\n🎉 All packages installed successfully!")
        print("💡 You can now run: python main.py")
    else:
        print("\n⚠️ Some packages failed to install.")
        print("💡 Try running the failed installations manually.")
        
    input("\nPress Enter to exit...")
