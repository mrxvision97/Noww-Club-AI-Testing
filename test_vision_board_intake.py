#!/usr/bin/env python3
"""
Test script for the new vision board intake system
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_vision_board_intake():
    """Test the vision board intake system"""
    try:
        print("🧪 Testing Vision Board Intake System...")
        
        # Test imports
        print("📦 Testing imports...")
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.vision_board_intake import VisionBoardIntakeManager
        print("✅ All imports successful")
        
        # Test initialization
        print("🔧 Testing initialization...")
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
        print("✅ All components initialized")
        
        # Test questions
        print("❓ Testing questions...")
        print(f"📝 Total questions: {len(intake_manager.questions)}")
        for i, q_data in intake_manager.questions.items():
            print(f"   Q{i}: {q_data['theme']} - {q_data['question'][:50]}...")
        
        # Test flow start
        print("🚀 Testing flow start...")
        test_user_id = "test_intake_user"
        start_message = intake_manager.start_intake_flow(test_user_id)
        print(f"✅ Flow started successfully")
        print(f"📄 Start message length: {len(start_message)} chars")
        
        # Test status check
        print("📊 Testing status check...")
        status = intake_manager.get_intake_status(test_user_id)
        print(f"✅ Status: {status}")
        
        print("\n🎉 All tests passed! Vision board intake system is ready.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vision_board_intake()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
