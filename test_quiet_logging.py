#!/usr/bin/env python3
"""
Test script to verify logging configuration is working
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment and configure logging
from dotenv import load_dotenv
load_dotenv()

from core.logging_config import setup_logging
setup_logging()  # This will use LOG_LEVEL from .env

def test_verbose_libraries():
    """Test that verbose libraries are now quiet"""
    print("🧪 Testing logging configuration...")
    
    # Test httpx (OpenAI API calls)
    import logging
    httpx_logger = logging.getLogger('httpx')
    httpx_logger.info("This httpx INFO should NOT appear")
    httpx_logger.warning("This httpx WARNING should appear")
    
    # Test apscheduler
    apscheduler_logger = logging.getLogger('apscheduler.executors.default')
    apscheduler_logger.info("This scheduler INFO should NOT appear")
    apscheduler_logger.error("This scheduler ERROR should appear")
    
    # Test app loggers
    app_logger = logging.getLogger('core.test')
    app_logger.info("This app INFO may or may not appear (depends on LOG_LEVEL)")
    app_logger.warning("This app WARNING should appear")
    
    print("✅ Logging test complete!")
    print("📋 Summary:")
    print("   - httpx/OpenAI API logs: Reduced to WARNING+ only")
    print("   - apscheduler logs: Reduced to ERROR only") 
    print("   - App logs: Controlled by LOG_LEVEL in .env")
    print(f"   - Current LOG_LEVEL: {os.getenv('LOG_LEVEL', 'WARNING')}")

def test_memory_with_reduced_logging():
    """Test that memory operations have reduced logging"""
    print("\n🧠 Testing memory operations with reduced logging...")
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        
        print("📦 Initializing memory system...")
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        print("✅ Memory system initialized")
        
        # This should create embeddings but with minimal logs
        print("💾 Testing memory storage (should be less verbose now)...")
        user_id = "test_quiet_logging"
        memory_manager.add_interaction(
            user_id=user_id,
            human_message="Testing if logging is now quieter",
            ai_message="Yes, the verbose httpx and scheduler logs should be suppressed now!"
        )
        print("✅ Memory operation completed with reduced logging")
        
    except Exception as e:
        print(f"❌ Error testing memory: {e}")

if __name__ == "__main__":
    test_verbose_libraries()
    test_memory_with_reduced_logging()
