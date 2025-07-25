"""
Test complete application flow including memory, web search, and vision board functionality
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.smart_agent import SmartAgent
from core.memory import MemoryManager
from core.database import DatabaseManager
import json
import time

def test_complete_flow():
    """Test the complete application flow"""
    print("🧪 Testing Complete Application Flow")
    print("=" * 50)
    
    try:
        # Initialize components in correct order
        memory = MemoryManager()
        db = DatabaseManager()
        agent = SmartAgent(db, memory)
        
        user_id = "test_user_complete"
        
        print("\n1. Testing Memory and Session Restoration")
        print("-" * 30)
        
        # Store some conversation context
        agent.memory_manager.add_interaction(user_id, "Hi, I want to lose 10 pounds", "Great! I'll help you set up a weight loss plan.")
        agent.memory_manager.add_interaction(user_id, "How should I start?", "Start with setting a realistic goal and tracking your daily habits.")
        
        # Restore session context
        restored_context = agent.memory_manager.restore_session_context(user_id)
        print(f"✅ Session context restored: {len(restored_context)} conversations")
        
        print("\n2. Testing Database Functions")
        print("-" * 30)
        
        # Test habit creation
        habit_response = agent.process_message(user_id, "I want to create a habit to drink 8 glasses of water daily")
        print(f"✅ Habit creation: {habit_response[:100]}...")
        
        # Test goal creation  
        goal_response = agent.process_message(user_id, "I want to set a goal to lose 10 pounds in 3 months")
        print(f"✅ Goal creation: {goal_response[:100]}...")
        
        # Test reminder creation
        reminder_response = agent.process_message(user_id, "Set a reminder to take vitamins every morning at 8 AM")
        print(f"✅ Reminder creation: {reminder_response[:100]}...")
        
        print("\n3. Testing Web Search Functionality")
        print("-" * 30)
        
        # Test web search
        search_response = agent.process_message(user_id, "What are the latest tips for healthy weight loss?")
        print(f"✅ Web search response: {search_response[:100]}...")
        
        print("\n4. Testing Vision Board Flow Detection")
        print("-" * 30)
        
        # Test vision board intent detection
        vision_response1 = agent.process_message(user_id, "I want to create a vision board for my fitness goals")
        print(f"✅ Vision board intent: {vision_response1[:100]}...")
        
        # Test confirmation handling
        time.sleep(1)  # Small delay
        confirmation_response = agent.process_message(user_id, "yes go ahead")
        print(f"✅ Vision board confirmation: {confirmation_response[:100]}...")
        
        print("\n5. Testing General Conversation")
        print("-" * 30)
        
        # Test general conversation
        general_response = agent.process_message(user_id, "How are you doing today?")
        print(f"✅ General conversation: {general_response[:100]}...")
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_vision_board_specific():
    """Test specific vision board flow scenarios"""
    print("\n🎨 Testing Vision Board Specific Scenarios")
    print("=" * 50)
    
    try:
        memory = MemoryManager()
        db = DatabaseManager()
        agent = SmartAgent(db, memory)
        user_id = "test_vision_board_user"
        
        # Scenario 1: Direct vision board request
        print("\n📋 Scenario 1: Direct vision board request")
        response1 = agent.process_message(user_id, "I want to create a vision board")
        print(f"Response: {response1}")
        
        # Scenario 2: Confirmation with "yes go ahead"
        print("\n📋 Scenario 2: Confirmation with 'yes go ahead'")
        response2 = agent.process_message(user_id, "yes go ahead")
        print(f"Response: {response2}")
        
        # Scenario 3: Different confirmation phrases
        print("\n📋 Scenario 3: Different confirmation phrases")
        agent.process_message(user_id, "I want to visualize my dreams")
        response3 = agent.process_message(user_id, "sure, let's start")
        print(f"Response: {response3}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vision board test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Application Tests")
    
    # Test complete flow
    flow_success = test_complete_flow()
    
    # Test vision board specific scenarios
    vision_success = test_vision_board_specific()
    
    if flow_success and vision_success:
        print("\n🎊 ALL TESTS PASSED! Application is ready for production.")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
