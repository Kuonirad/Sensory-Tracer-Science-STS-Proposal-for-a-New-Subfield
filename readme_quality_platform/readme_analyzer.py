#!/usr/bin/env python3
"""
README Quality Platform CLI Tool
"""

import sys
from pathlib import Path

# Add platform to path
platform_dir = Path(__file__).parent
sys.path.insert(0, str(platform_dir))

try:
    from cli.main import app
    
    if __name__ == "__main__":
        app()
        
except ImportError as e:
    print(f"Error: Could not start CLI tool: {e}")
    print("Make sure all dependencies are installed: pip install typer rich")
    sys.exit(1)
