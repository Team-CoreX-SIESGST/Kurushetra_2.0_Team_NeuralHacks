#!/usr/bin/env python3
"""
Debug script to check environment variables and API configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def debug_environment():
    """Debug environment configuration"""
    print("🔧 Environment Variables Debug")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📄 .env file exists: {env_file.exists()}")
    print(f"📄 .env.example exists: {env_example.exists()}")
    
    if env_file.exists():
        print(f"📏 .env file size: {env_file.stat().st_size} bytes")
        
        # Read .env content (safely)
        print("\n📋 .env file content:")
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if "GEMINI_API_KEY" in line:
                        if "=" in line:
                            key, value = line.split("=", 1)
                            masked_value = value.strip()
                            if masked_value and masked_value != "your_gemini_api_key_here":
                                masked_value = masked_value[:10] + "..." + masked_value[-5:]
                            print(f"  Line {i}: {key.strip()}={masked_value}")
                        else:
                            print(f"  Line {i}: {line.strip()} (⚠️ Missing '=')")
                    else:
                        print(f"  Line {i}: {line.strip()}")
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
    
    # Load environment variables
    print(f"\n🔄 Loading environment variables...")
    load_dotenv()
    
    # Check environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    print(f"🔑 GEMINI_API_KEY from environment:")
    
    if gemini_key:
        if gemini_key == "your_gemini_api_key_here":
            print("  ⚠️ Still using placeholder value!")
            print("  📝 Please replace with your actual Gemini API key")
        elif len(gemini_key) < 10:
            print(f"  ⚠️ API key seems too short: '{gemini_key}'")
        else:
            masked_key = gemini_key[:10] + "..." + gemini_key[-5:]
            print(f"  ✅ API key loaded: {masked_key}")
            print(f"  📏 Length: {len(gemini_key)} characters")
    else:
        print("  ❌ GEMINI_API_KEY not found in environment")
    
    # Test RAG system initialization
    print(f"\n🤖 Testing RAG system...")
    try:
        from rag_system import RAGSystem
        rag = RAGSystem()
        status = rag.check_api_status()
        print(f"  🔍 RAG system API status: {status}")
        
        if status == "not_configured":
            print("  💡 Suggestions:")
            print("     1. Make sure .env file is in the same directory as main.py")
            print("     2. Check that GEMINI_API_KEY=your_actual_key (no spaces)")
            print("     3. Restart the application after updating .env")
            print("     4. Get API key from: https://makersuite.google.com/")
        
    except Exception as e:
        print(f"  ❌ Error testing RAG system: {e}")
    
    # Environment variable check
    print(f"\n📊 All environment variables:")
    env_vars = ["GEMINI_API_KEY", "HOST", "PORT", "DEBUG"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var and len(value) > 10:
                masked = value[:5] + "..." + value[-3:]
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")

def fix_env_file():
    """Help fix .env file"""
    print(f"\n🛠️ Environment File Fixer")
    print("=" * 30)
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        
        env_example = Path(".env.example")
        if env_example.exists():
            print("📄 Copying .env.example to .env...")
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ .env file created!")
        else:
            print("📝 Creating .env file...")
            with open(env_file, 'w') as f:
                f.write("# Gemini API Configuration\n")
                f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
                f.write("\n# Server Configuration\n")
                f.write("HOST=0.0.0.0\n")
                f.write("PORT=8000\n")
                f.write("DEBUG=True\n")
            print("✅ .env file created!")
    
    print("\n📝 To fix your API key:")
    print("1. Open .env file in a text editor")
    print("2. Replace 'your_gemini_api_key_here' with your actual API key")
    print("3. Save the file")
    print("4. Restart the application")
    print("\n🔗 Get API key from: https://makersuite.google.com/")

if __name__ == "__main__":
    debug_environment()
    
    # Ask if user wants to fix .env
    print("\n" + "=" * 50)
    try:
        fix_it = input("Do you want to create/fix .env file? (y/n): ").lower().strip()
        if fix_it == 'y':
            fix_env_file()
    except KeyboardInterrupt:
        print("\n👋 Debug session ended.")
