#!/usr/bin/env python3
"""
Test script to demonstrate cloud logging output for Render deployment
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our cloud logging system
from core.cloud_logging import cloud_logger

def test_cloud_logging():
    """Test the cloud logging system to show how it will appear in Render"""
    
    # Test startup banner
    cloud_logger.log_startup_info()
    
    # Simulate component initialization
    print("\n🔧 COMPONENT INITIALIZATION TEST")
    print("-" * 60)
    
    # Test successful component
    cloud_logger.log_component_status("Database Manager", "SUCCESS", "SQLite database ready")
    time.sleep(0.5)
    
    # Test memory system with different states
    if os.getenv('PINECONE_API_KEY'):
        cloud_logger.log_memory_status(True, "Connected to cloud vector database")
    else:
        cloud_logger.log_memory_status(False, "Using local file storage")
    time.sleep(0.5)
    
    # Test other components
    cloud_logger.log_component_status("Smart Agent", "SUCCESS", "GPT-4o ready")
    time.sleep(0.3)
    cloud_logger.log_component_status("Auth Manager", "SUCCESS", "Authentication ready")
    time.sleep(0.3)
    cloud_logger.log_component_status("Voice Handler", "WARNING", "Non-critical: Audio permissions needed")
    time.sleep(0.3)
    
    # Test environment check
    required_missing = []
    optional_missing = ["GOOGLE_CLIENT_ID (Google OAuth)", "SUPABASE_URL (Database auth)"]
    
    if not os.getenv('OPENAI_API_KEY'):
        required_missing.append('OPENAI_API_KEY')
    
    cloud_logger.log_environment_check(required_missing, optional_missing)
    
    # Test final ready status
    cloud_logger.log_app_ready(6)
    
    print("\n" + "="*70)
    print("✅ CLOUD LOGGING TEST COMPLETE")
    print("This is how your logs will appear in Render's CLI and dashboard!")
    print("="*70)

if __name__ == "__main__":
    print("🧪 Testing Cloud Logging System for Render Deployment")
    print("="*70)
    test_cloud_logging()
