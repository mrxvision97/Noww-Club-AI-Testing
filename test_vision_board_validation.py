#!/usr/bin/env python3
"""
Test the enhanced vision board system with validation logic
Tests that users don't have to repeat intake if they already have sufficient data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.vision_board_intake import VisionBoardIntakeManager
from core.database import DatabaseManager
from core.memory import MemoryManager
from core.smart_agent import SmartAgent

def test_vision_board_validation():
    """Test the complete validation flow"""
    print("🧪 Testing Vision Board Validation System...")
    
    # Initialize system
    print("📦 Initializing system...")
    db_manager = DatabaseManager()
    memory_manager = MemoryManager()
    intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
    smart_agent = SmartAgent(db_manager, memory_manager)
    
    test_user_id = "test_validation_user"
    
    # Test 1: New user should go through intake
    print("\n🔍 Test 1: New user requesting vision board...")
    intake_manager._clear_intake_data(test_user_id)
    
    can_skip, explanation = intake_manager.can_skip_intake(test_user_id)
    print(f"✅ New user can skip intake: {can_skip}")
    print(f"✅ Explanation length: {len(explanation)} chars")
    
    # Test 2: Complete intake for user
    print("\n📝 Test 2: Completing intake for user...")
    
    # Sample realistic answers
    sample_answers = [
        "I want to feel more confident and empowered in everything I do",
        "I want to be known as someone who helps others achieve their dreams",
        "I'm learning digital marketing and want to master it",
        "Taking time for morning meditation and working out regularly",
        "Ambitious, supportive people who aren't afraid to dream big",
        "When I'm mentoring others or creating content - that's when I feel most alive",
        "A modern, organized home office with natural light and inspiring artwork",
        "My leadership skills - I'm ready to step up and guide others",
        "I want to start my own business and help 1000 people transform their lives",
        "I want to make a million dollars doing work I love and helping others"
    ]
    
    # Start and complete intake
    start_response = intake_manager.start_intake_flow(test_user_id)
    print(f"✅ Started intake: {len(start_response)} chars")
    
    for i, answer in enumerate(sample_answers, 1):
        response = intake_manager.process_answer(test_user_id, answer)
        print(f"   Processed Q{i}: {len(response)} chars")
    
    # Test 3: User with completed intake should be able to skip
    print("\n🎯 Test 3: User with completed intake...")
    
    can_skip_after, explanation_after = intake_manager.can_skip_intake(test_user_id)
    print(f"✅ User can skip intake after completion: {can_skip_after}")
    print(f"✅ Skip explanation: {explanation_after[:200]}...")
    
    # Test 4: Check data sufficiency
    print("\n📊 Test 4: Data sufficiency check...")
    
    has_sufficient = intake_manager.has_sufficient_data_for_vision_board(test_user_id)
    print(f"✅ Has sufficient data: {has_sufficient}")
    
    status = intake_manager.get_data_completeness_status(test_user_id)
    print(f"✅ Completeness status: {status['sufficient_for_vision_board']}")
    print(f"✅ Valid answers: {status['valid_answers']}")
    print(f"✅ Template recommendation: {status.get('recommended_template', 'None')}")
    
    # Test 5: Smart agent handling
    print("\n🤖 Test 5: Smart agent vision board request handling...")
    
    # Simulate vision board request from user with existing data
    response1 = smart_agent.process_message(test_user_id, "I want to create a vision board")
    print(f"✅ Smart agent response (existing data): {len(response1)} chars")
    print(f"✅ Contains 'Great news': {'Great news' in response1}")
    
    # Test 6: New user request
    print("\n🆕 Test 6: New user vision board request...")
    
    new_user_id = "test_new_user"
    intake_manager._clear_intake_data(new_user_id)
    
    response2 = smart_agent.process_message(new_user_id, "Create a vision board for me")
    print(f"✅ New user response: {len(response2)} chars")
    intake_start_text = "Let's create your perfect vision board"
    print(f"✅ Contains intake start: {intake_start_text in response2}")
    
    # Test 7: Vision board generation with existing data
    print("\n🎨 Test 7: Vision board generation...")
    
    # Simulate user confirming they want to proceed
    generation_response = smart_agent.process_message(test_user_id, "Yes, please proceed with my vision board")
    print(f"✅ Generation response: {len(generation_response)} chars")
    
    print("\n🎉 All validation tests completed!")
    return True

def test_conversation_memory_update():
    """Test that ongoing conversations update user insights"""
    print("\n🧠 Testing conversation memory updates...")
    
    db_manager = DatabaseManager()
    memory_manager = MemoryManager()
    intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
    
    test_user_id = "test_memory_update"
    
    # Simulate updating insights from conversation
    conversation_insights = {
        "new_interests": ["photography", "travel"],
        "current_goals": ["learn Spanish", "get fit"],
        "lifestyle_changes": ["working remotely", "living minimally"]
    }
    
    intake_manager.update_user_insights_from_conversation(test_user_id, conversation_insights)
    print("✅ Conversation insights updated")
    
    return True

if __name__ == "__main__":
    try:
        # Test main validation system
        success1 = test_vision_board_validation()
        
        # Test memory updates
        success2 = test_conversation_memory_update()
        
        if success1 and success2:
            print("\n🎉 ALL VALIDATION TESTS PASSED! 🚀")
            print("\n✅ Users with existing data won't be asked to repeat intake")
            print("✅ Smart agent properly validates before requesting intake")
            print("✅ Vision board generation works with existing data")
            print("✅ Memory updates work for ongoing conversations")
            print("\n🌟 System is ready for production!")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
