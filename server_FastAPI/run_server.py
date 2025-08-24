#!/usr/bin/env python3
"""
OmniSearch AI Server Startup Script
Enhanced script to start the FastAPI server with resource-aware configuration
and safe demo mode for local laptop execution.
"""

import os
import sys
import subprocess
import platform
import argparse
import psutil
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import motor
        import google.generativeai
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment is properly configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please copy example_env.txt to .env and configure it")
        return False
    
    print("✅ Environment file found")
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting OmniSearch AI Server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")


def start_server_with_options(args) -> None:
    """Start the FastAPI server with custom options."""
    print("🚀 Starting OmniSearch AI Server...")
    print(f"Server will be available at: http://{args.host}:{args.port}")
    print(f"API Documentation: http://{args.host}:{args.port}/docs")
    print(f"Alternative Docs: http://{args.host}:{args.port}/redoc")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Build uvicorn command
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app",
            "--host", args.host,
            "--port", str(args.port),
            "--log-level", args.log_level
        ]
        
        # Add reload flag unless disabled
        if not args.no_reload:
            cmd.append("--reload")
        
        # Start server
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def check_system_resources() -> dict:
    """Quick system resource check."""
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    cpu_cores = psutil.cpu_count(logical=True)
    
    return {
        'available_ram_gb': round(available_gb, 1),
        'cpu_cores': cpu_cores,
        'safe_mode_recommended': available_gb < 6
    }


def apply_safe_demo_overrides(args) -> None:
    """Apply safe demo mode environment overrides."""
    overrides = {}
    
    if args.safe_demo:
        overrides.update({
            'SAFE_DEMO_MODE': 'true',
            'ENABLE_RESOURCE_GUARD': 'true',
            'MAX_CONCURRENCY': '1',
            'QUEUE_MAX_WORKERS': '1'
        })
    
    if args.skip_embeddings:
        overrides['ENABLE_EMBEDDINGS'] = 'false'
    
    if args.skip_rerank:
        overrides['ENABLE_RERANK'] = 'false'
    
    if args.skip_summarizer:
        overrides['ENABLE_SUMMARIZER'] = 'false'
    
    if args.no_models:
        overrides.update({
            'ENABLE_EMBEDDINGS': 'false',
            'ENABLE_RERANK': 'false',
            'ENABLE_SUMMARIZER': 'false'
        })
    
    # Apply overrides to environment
    for key, value in overrides.items():
        os.environ[key] = value
    
    return overrides


def print_startup_summary(args, resource_info: dict, overrides: dict) -> None:
    """Print startup configuration summary."""
    print("\n🚀 STARTUP CONFIGURATION:")
    print("-" * 40)
    print(f"System RAM: {resource_info['available_ram_gb']}GB available")
    print(f"CPU Cores: {resource_info['cpu_cores']}")
    
    if resource_info['safe_mode_recommended']:
        print("⚠️  Safe mode recommended (< 6GB RAM)")
    
    # Show active flags
    active_flags = []
    if args.safe_demo:
        active_flags.append('--safe-demo')
    if args.skip_embeddings:
        active_flags.append('--skip-embeddings')
    if args.skip_rerank:
        active_flags.append('--skip-rerank')
    if args.skip_summarizer:
        active_flags.append('--skip-summarizer')
    if args.no_models:
        active_flags.append('--no-models')
    
    if active_flags:
        print(f"Active flags: {' '.join(active_flags)}")
    
    # Show applied overrides
    if overrides:
        print("\n🛡️  Active protections:")
        for key, value in overrides.items():
            print(f"  {key}={value}")


def main():
    """Enhanced main function with CLI arguments."""
    parser = argparse.ArgumentParser(
        description='OmniSearch AI Server with safe execution modes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Safe execution modes:
  --safe-demo         Enable comprehensive safe mode
  --skip-embeddings   Disable embedding generation (ultra-safe)
  --skip-rerank       Disable reranking (moderate RAM savings)
  --skip-summarizer   Disable summarization (moderate RAM savings)
  --no-models         Disable all AI model processing

Examples:
  python run_server.py                    # Standard mode
  python run_server.py --safe-demo        # Safe mode for <6GB RAM
  python run_server.py --skip-rerank      # Skip memory-intensive reranking
  python run_server.py --no-models        # Ultra-lightweight mode
        """
    )
    
    # Safety flags
    parser.add_argument('--safe-demo', action='store_true', 
                       help='Enable safe demo mode (resource guards, conservative settings)')
    parser.add_argument('--skip-embeddings', action='store_true',
                       help='Skip embedding generation (ultra-safe for very low RAM)')
    parser.add_argument('--skip-rerank', action='store_true',
                       help='Skip reranking (saves memory and CPU)')
    parser.add_argument('--skip-summarizer', action='store_true',
                       help='Skip summarization (saves memory and CPU)')
    parser.add_argument('--no-models', action='store_true',
                       help='Disable all AI model processing (ultra-lightweight)')
    
    # Server options
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload')
    parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'],
                       help='Logging level (default: info)')
    
    # Diagnostic options
    parser.add_argument('--check-resources', action='store_true',
                       help='Check system resources and exit')
    parser.add_argument('--generate-env', action='store_true',
                       help='Generate optimized .env and exit')
    
    args = parser.parse_args()
    
    # Handle diagnostic options
    if args.check_resources or args.generate_env:
        if Path('diagnose_resources.py').exists():
            cmd = [sys.executable, 'diagnose_resources.py']
            if args.generate_env:
                cmd.append('--generate-env')
            subprocess.run(cmd)
        else:
            print("❌ diagnose_resources.py not found")
        sys.exit(0)
    
    print("🔧 OmniSearch AI Server Setup")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Working directory: {current_dir}")
    
    # Check if we're in the right directory
    if not Path("app/main.py").exists():
        print("❌ Please run this script from the server_FastAPI directory")
        print("Current directory should contain app/main.py")
        sys.exit(1)
    
    # Check system resources
    resource_info = check_system_resources()
    
    # Auto-enable safe mode for low RAM systems
    if resource_info['safe_mode_recommended'] and not args.safe_demo:
        print(f"⚠️  Auto-enabling safe mode ({resource_info['available_ram_gb']}GB RAM < 6GB threshold)")
        args.safe_demo = True
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Apply safe demo overrides
    overrides = apply_safe_demo_overrides(args)
    
    # Import settings after environment overrides
    from app.settings import settings
    
    # Show configuration summary
    print_startup_summary(args, resource_info, overrides)
    
    # Show demo mode status
    if hasattr(settings, 'demo_mode') and settings.demo_mode.lower() == 'true':
        print("🎭 Demo mode enabled - authentication bypassed for testing")
    
    print("\n✅ All checks passed!")
    
    # Auto-start for non-interactive environments or with flags
    if not sys.stdin.isatty() or any([args.safe_demo, args.skip_embeddings, args.skip_rerank, args.no_models]):
        print("Auto-starting server...")
    else:
        input("Press Enter to start the server...")
    
    # Start server with custom options
    start_server_with_options(args)

if __name__ == "__main__":
    main()
