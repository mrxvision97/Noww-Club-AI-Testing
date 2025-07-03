#!/usr/bin/env python3
"""
Test script for web search functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.smart_agent import SmartAgent
from core.database import DatabaseManager
from core.memory import MemoryManager

def test_web_search():
    """Test the web search functionality"""
    print("Testing Web Search Functionality...")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set. Please set it in .env file.")
        return False
    
    try:
        # Initialize components
        print("✅ Initializing DatabaseManager...")
        db_manager = DatabaseManager()
        
        print("✅ Initializing MemoryManager...")
        memory_manager = MemoryManager(db_manager)
        
        print("✅ Initializing SmartAgent...")
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        # Test user ID
        test_user_id = "test_user_search"
        
        print(f"✅ Testing web search for user: {test_user_id}")
        
        # Test search queries
        test_queries = [
            "What is the latest news about Python programming?",
            "Current weather in New York",
            "Latest developments in AI technology"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}: Searching for '{query}'")
            try:
                result = smart_agent.search_and_respond(test_user_id, query)
                print(f"✅ Search completed successfully")
                print(f"📄 Result preview: {result[:200]}...")
                
                if len(result) > 50:  # Basic check that we got a meaningful response
                    print("✅ Response seems valid")
                else:
                    print("⚠️  Response seems short, might be an error")
                    
            except Exception as e:
                print(f"❌ Search failed: {e}")
                return False
        
        print("\n🎉 All web search tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_web_search()
    if success:
        print("\n✅ Web search functionality is working correctly!")
    else:
        print("\n❌ Web search functionality test failed!")
        sys.exit(1)
