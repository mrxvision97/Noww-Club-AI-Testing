#!/usr/bin/env python3
"""
Deployment Health Check for Render
This script runs after deployment to verify all systems are operational
"""

import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def log_deployment_status():
    """Log comprehensive deployment status for Render logs"""
    
    print("=" * 80)
    print("🚀 NOWW CLUB AI - DEPLOYMENT HEALTH CHECK")
    print("=" * 80)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print(f"🌐 Environment: {'Render Cloud' if os.getenv('RENDER') else 'Local'}")
    print(f"🖥️  Platform: {sys.platform}")
    print(f"🐍 Python: {sys.version}")
    print(f"📂 Working Dir: {os.getcwd()}")
    print("=" * 80)
    
    # Check critical environment variables
    print("\n🔍 ENVIRONMENT VARIABLES CHECK")
    print("-" * 60)
    
    critical_vars = {
        'OPENAI_API_KEY': 'OpenAI API access',
        'PINECONE_API_KEY': 'Vector memory storage',
        'RENDER': 'Cloud deployment flag',
        'PORT': 'Server port'
    }
    
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                masked_value = f"***{value[-4:]}" if len(value) > 4 else "***SET***"
                print(f"✅ {var:<20} | {description:<25} | {masked_value}")
            else:
                print(f"✅ {var:<20} | {description:<25} | {value}")
        else:
            print(f"❌ {var:<20} | {description:<25} | NOT_SET")
    
    print("-" * 60)
    
    # Test file system access
    print("\n📁 FILE SYSTEM CHECK")
    print("-" * 60)
    
    directories_to_check = [
        'user_profiles', 'vector_stores', 'logs', 'core', 'ui'
    ]
    
    for directory in directories_to_check:
        if os.path.exists(directory):
            print(f"✅ {directory:<20} | Directory exists")
        else:
            print(f"⚠️  {directory:<20} | Directory missing - will be created")
    
    # Test database file
    if os.path.exists('noww_club.db'):
        size = os.path.getsize('noww_club.db')
        print(f"✅ noww_club.db        | Database file exists ({size} bytes)")
    else:
        print(f"⚠️  noww_club.db        | Database file missing - will be created")
    
    print("-" * 60)
    
    # Test Python imports
    print("\n🐍 PYTHON IMPORTS CHECK")
    print("-" * 60)
    
    critical_imports = [
        ('streamlit', 'Web framework'),
        ('openai', 'AI API client'),
        ('pinecone', 'Vector database'),
        ('langchain', 'AI framework'),
        ('sqlite3', 'Database')
    ]
    
    for module, description in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module:<20} | {description:<25} | Imported successfully")
        except ImportError as e:
            print(f"❌ {module:<20} | {description:<25} | Import failed: {e}")
    
    print("-" * 60)
    
    # Test core modules
    print("\n🔧 CORE MODULES CHECK")
    print("-" * 60)
    
    core_modules = [
        'core.database',
        'core.memory', 
        'core.smart_agent',
        'core.auth',
        'ui.chat_interface'
    ]
    
    for module in core_modules:
        try:
            __import__(module)
            print(f"✅ {module:<25} | Core module imported successfully")
        except Exception as e:
            print(f"❌ {module:<25} | Import failed: {str(e)[:50]}...")
    
    print("-" * 60)
    
    # Final status
    print("\n🎯 DEPLOYMENT SUMMARY")
    print("=" * 80)
    
    if os.getenv('RENDER'):
        print("🌐 RENDER CLOUD DEPLOYMENT DETECTED")
        print("📊 Logs visible in Render dashboard")
        print("🔗 Application will be accessible via Render URL")
    else:
        print("🏠 LOCAL DEVELOPMENT ENVIRONMENT")
        print("📊 Logs visible in terminal")
        print("🔗 Application accessible at localhost")
    
    print("=" * 80)
    print("✅ HEALTH CHECK COMPLETE")
    print(f"🕐 Completed at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    log_deployment_status()
