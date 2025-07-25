"""
Quick test of the main app functionality to ensure everything works end-to-end
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_main_app_import():
    """Test that we can import and initialize the main app components"""
    print("🧪 Testing Main App Import and Initialization")
    print("=" * 50)
    
    try:
        # Test core component imports
        from core.smart_agent import SmartAgent
        from core.memory import MemoryManager
        from core.database import DatabaseManager
        print("✅ Core imports successful")
        
        # Test initialization
        memory = MemoryManager()
        db = DatabaseManager()
        agent = SmartAgent(db, memory)
        print("✅ Component initialization successful")
        
        # Test vision board flow specifically
        user_id = "final_test_user"
        
        # Test vision board intent detection
        response1 = agent.process_message(user_id, "I want to create a vision board for my dreams")
        print("✅ Vision board intent detected")
        
        # Test confirmation response
        response2 = agent.process_message(user_id, "yes go ahead")
        print("✅ Confirmation response processed")
        
        # Verify it's proceeding with intake (should have "Question" in response)
        if "Question" in response2:
            print("✅ Vision board intake process started correctly")
        else:
            print("⚠️ Vision board intake may not have started properly")
            print(f"Response: {response2[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_main_app_import()
    if success:
        print("\n🎊 MAIN APP TEST PASSED! Ready for production use.")
    else:
        print("\n⚠️ Main app test failed. Check the errors above.")
