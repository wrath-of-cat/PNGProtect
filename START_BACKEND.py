#!/usr/bin/env python
"""
Simple script to start the PNGProtect backend server.
Run this from the backend directory.
"""

import subprocess
import sys
import os

# Change to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(backend_dir, 'backend')

print("=" * 60)
print("PNGProtect Backend Server")
print("=" * 60)
print(f"Starting from: {backend_dir}")
print()

# Start uvicorn
try:
    os.chdir(backend_dir)
    subprocess.run([
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--reload',
        '--host', '127.0.0.1',
        '--port', '8000'
    ])
except KeyboardInterrupt:
    print("\n\nServer stopped.")
    sys.exit(0)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
