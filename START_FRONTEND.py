#!/usr/bin/env python
"""
Simple HTTP server to serve the frontend locally.
Run this from the project root directory.
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

# Setup
PORT = 8080
frontend_dir = Path(__file__).parent / "frontend"

# Change to frontend directory
os.chdir(frontend_dir)

# Create handler
Handler = http.server.SimpleHTTPRequestHandler

print("=" * 60)
print("PNGProtect Frontend Server")
print("=" * 60)
print(f"Serving from: {frontend_dir}")
print(f"Access URL: http://127.0.0.1:{PORT}")
print()
print("Press Ctrl+C to stop")
print()

# Start server
try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running on http://127.0.0.1:{PORT}")
        # Optionally open in browser
        try:
            webbrowser.open(f"http://127.0.0.1:{PORT}")
        except:
            pass
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n\nServer stopped.")
    sys.exit(0)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
