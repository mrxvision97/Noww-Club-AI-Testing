#!/usr/bin/env python3
"""
Interactive test script to demonstrate the memory and search system working together
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

def interactive_test():
    """Interactive test of the system"""
    print("🚀 Interactive Memory & Search Test")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set. Please set it in .env file.")
        return False
    
    try:
        # Initialize components
        print("✅ Initializing system components...")
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        test_user_id = "demo_user"
        print(f"✅ Ready! Testing with user: {test_user_id}")
        
        # Test 1: Add some personal information
        print("\n📝 Test 1: Adding personal information to memory")
        memory_manager.add_interaction(
            test_user_id,
            "Hi, I'm Sarah and I'm a software engineer. I love Python programming and working on AI projects.",
            "Nice to meet you, Sarah! It's great to connect with a fellow Python enthusiast. AI projects are fascinating - what kind of AI work are you most interested in?"
        )
        print("✅ Personal information added to memory")
        
        # Test 2: Add more context
        print("\n📝 Test 2: Adding more context")
        memory_manager.add_interaction(
            test_user_id,
            "I'm particularly interested in natural language processing and machine learning. I've been working with LangChain recently.",
            "That's excellent! LangChain is a powerful framework for building applications with language models. Are you working on any specific NLP projects right now?"
        )
        print("✅ More context added")
        
        # Test 3: Check memory context
        print("\n📝 Test 3: Checking memory context")
        context = memory_manager.get_context_for_conversation(test_user_id, "Tell me about my interests")
        print(f"📄 Context length: {len(context)} characters")
        print(f"📄 Context preview: {context[:300]}...")
        
        # Test 4: Web search with context
        print("\n📝 Test 4: Web search with personalized context")
        search_result = smart_agent.search_and_respond(test_user_id, "What are the latest developments in LangChain?")
        print(f"🔍 Search result preview: {search_result[:200]}...")
        
        # Test 5: Show memory persistence
        print("\n📝 Test 5: Memory persistence")
        memory_manager.save_memory_profile(test_user_id)
        
        # Create new instance to test persistence
        new_memory_manager = MemoryManager(db_manager)
        restored_memory = new_memory_manager.get_user_memory(test_user_id)
        print(f"📄 Restored memory - Messages: {len(restored_memory['short_term_messages'])}")
        print(f"📄 Restored memory - Profile keys: {list(restored_memory['profile'].keys())}")
        
        print("\n🎉 All interactive tests completed successfully!")
        print("\n📊 System Features Demonstrated:")
        print("   ✅ Memory system with personal information storage")
        print("   ✅ Context-aware conversation memory")
        print("   ✅ Web search with personalized context")
        print("   ✅ Memory persistence and restoration")
        print("   ✅ Integration between memory and search systems")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = interactive_test()
    if success:
        print("\n✅ Interactive test completed successfully!")
    else:
        print("\n❌ Interactive test failed!")
        sys.exit(1)
