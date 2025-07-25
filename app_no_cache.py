"""
Cache-safe version of the Streamlit app to avoid file watcher issues
"""
import sys
import os

# Disable Python bytecode generation
sys.dont_write_bytecode = True

# Clear any existing cache
import shutil
cache_dirs = ['__pycache__', 'core/__pycache__', 'ui/__pycache__', 'utils/__pycache__']
for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
        except:
            pass

# Import and run the main app
from app import main

if __name__ == "__main__":
    main()
