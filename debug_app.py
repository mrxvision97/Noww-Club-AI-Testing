#!/usr/bin/env python3
"""
Debug script to identify the shutdown issue
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_components():
    """Test component initialization"""
    try:
        print("Starting component test...")
        
        # Test imports
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.smart_agent import SmartAgent
        print("✅ All imports successful")
        
        # Test database
        db_manager = DatabaseManager()
        print("✅ Database manager initialized")
        
        # Test memory manager
        memory_manager = MemoryManager(db_manager)
        print("✅ Memory manager initialized")
        
        # Test smart agent
        if os.getenv('OPENAI_API_KEY'):
            smart_agent = SmartAgent(db_manager, memory_manager)
            print("✅ Smart agent initialized")
            
            # Test a simple message processing
            try:
                test_user_id = "test_user"
                test_message = "Hello, how are you?"
                
                print(f"Testing message processing for user: {test_user_id}")
                print(f"Message: {test_message}")
                
                response = smart_agent.process_message(test_user_id, test_message)
                print(f"✅ Message processed successfully")
                print(f"Response length: {len(response)} characters")
                
            except Exception as e:
                print(f"❌ Error in message processing: {e}")
                import traceback
                traceback.print_exc()
                return False
                
        else:
            print("⚠️  No OpenAI API key found - skipping smart agent test")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in component initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_components()
    if success:
        print("\n✅ All components working correctly")
    else:
        print("\n❌ Component test failed")
        sys.exit(1)
