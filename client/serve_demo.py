#!/usr/bin/env python3
"""
Simple HTTP server to serve the demo.html file
This avoids CORS issues when accessing the API from a web browser
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def serve_demo(port=3000):
    """Serve the demo.html file on localhost"""
    
    # Change to the client directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"🌐 Starting demo server...")
    print(f"📁 Serving from: {script_dir}")
    print(f"🔗 Demo URL: http://localhost:{port}")
    print(f"📄 Main file: demo.html")
    print(f"🚀 API Server: http://localhost:8000")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            print(f"✅ Server started successfully!")
            print(f"🌍 Open your browser to: http://localhost:{port}/demo.html")
            print("🛑 Press Ctrl+C to stop the server")
            print()
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{port}/demo.html')
                print("🔗 Browser opened automatically!")
            except:
                print("⚠️  Could not open browser automatically")
                
            print("\n" + "=" * 50)
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Try a different port:")
            print(f"   python serve_demo.py --port 3001")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
        sys.exit(0)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Serve OmniSearch AI Demo')
    parser.add_argument('--port', type=int, default=3000, 
                       help='Port to serve on (default: 3000)')
    
    args = parser.parse_args()
    serve_demo(args.port)

if __name__ == "__main__":
    main()
