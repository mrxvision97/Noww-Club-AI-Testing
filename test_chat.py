#!/usr/bin/env python3
"""
Test script to simulate user interaction and see if the app shuts down
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_message_processing():
    """Test message processing without Streamlit"""
    try:
        print("Testing message processing...")
        
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.smart_agent import SmartAgent
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        print("✅ All components initialized")
        
        # Test a conversation
        user_id = "test_user_123"
        messages = [
            "Hello, how are you?",
            "What's the weather like?",
            "Can you remember that I like pizza?",
            "What do you remember about me?"
        ]
        
        for i, message in enumerate(messages, 1):
            print(f"\n📝 Testing message {i}: {message}")
            
            try:
                response = smart_agent.process_message(user_id, message)
                print(f"✅ Response received ({len(response)} chars)")
                print(f"   Preview: {response[:100]}...")
                
            except Exception as e:
                print(f"❌ Error processing message {i}: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print("\n✅ All messages processed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_message_processing()
    if success:
        print("\n🎉 Message processing test passed!")
        print("The chatbot should work correctly in the Streamlit app.")
    else:
        print("\n💥 Message processing test failed!")
        sys.exit(1)
