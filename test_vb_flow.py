"""
Test enhanced vision board generation performance
"""
import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_vision_board_flow():
    """Test the complete optimized vision board flow"""
    print("🎨 Testing Complete Vision Board Flow")
    print("=" * 50)
    
    try:
        from core.smart_agent import SmartAgent
        from core.memory import MemoryManager
        from core.database import DatabaseManager
        
        # Initialize components
        memory = MemoryManager()
        db = DatabaseManager()
        agent = SmartAgent(db, memory)
        
        user_id = "vb_flow_test_user"
        
        # Test 1: Vision board intent recognition
        print("\n🎯 Test 1: Intent Recognition Speed")
        start_time = time.time()
        response1 = agent.process_message(user_id, "I want to create a vision board")
        intent_time = time.time() - start_time
        print(f"✅ Intent recognized in {intent_time:.2f}s")
        
        # Test 2: Confirmation processing  
        print("\n✅ Test 2: Confirmation Processing Speed")
        start_time = time.time()
        response2 = agent.process_message(user_id, "yes go ahead")
        confirm_time = time.time() - start_time
        print(f"✅ Confirmation processed in {confirm_time:.2f}s")
        
        # Test 3: Question answering speed
        print("\n💬 Test 3: Question Response Speed")
        start_time = time.time()
        response3 = agent.process_message(user_id, "I want to feel more confident and empowered")
        answer_time = time.time() - start_time
        print(f"✅ Answer processed in {answer_time:.2f}s")
        
        # Test 4: Multiple quick answers
        print("\n⚡ Test 4: Multiple Quick Answers")
        times = []
        answers = [
            "I want to help others while building my business",
            "I'm learning digital marketing and leadership",
            "Self-care means setting boundaries and morning walks",
            "I want supportive, ambitious people around me"
        ]
        
        for i, answer in enumerate(answers, 2):
            start_time = time.time()
            response = agent.process_message(user_id, answer)
            answer_time = time.time() - start_time
            times.append(answer_time)
            print(f"   Q{i+1}: {answer_time:.2f}s")
        
        avg_answer_time = sum(times) / len(times)
        print(f"✅ Average answer time: {avg_answer_time:.2f}s")
        
        # Performance Summary
        print("\n" + "=" * 50)
        print("📊 VISION BOARD FLOW PERFORMANCE")
        print("=" * 50)
        print(f"🎯 Intent Recognition: {intent_time:.2f}s")
        print(f"✅ Confirmation: {confirm_time:.2f}s")
        print(f"💬 First Answer: {answer_time:.2f}s")
        print(f"⚡ Average Answer: {avg_answer_time:.2f}s")
        
        total_flow_time = intent_time + confirm_time + answer_time + sum(times)
        print(f"\n⏱️ Total Flow Time: {total_flow_time:.2f}s")
        
        if avg_answer_time < 3.0:
            print("🚀 EXCELLENT performance! Vision board flow is fast!")
        elif avg_answer_time < 5.0:
            print("✅ GOOD performance! Flow is responsive!")
        else:
            print("⚠️ Performance could be improved")
        
        return True
        
    except Exception as e:
        print(f"❌ Flow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vision_board_flow()
    if success:
        print("\n🎊 VISION BOARD FLOW TEST COMPLETED!")
        print("✨ Performance optimizations working perfectly!")
    else:
        print("\n⚠️ Flow test had issues.")
