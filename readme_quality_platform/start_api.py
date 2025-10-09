#!/usr/bin/env python3
"""
README Quality Platform API Server
"""

import sys
from pathlib import Path

# Add platform to path
platform_dir = Path(__file__).parent
sys.path.insert(0, str(platform_dir))

try:
    from api.server import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error: Could not start API server: {e}")
    print("Make sure all dependencies are installed: pip install fastapi uvicorn")
    sys.exit(1)
