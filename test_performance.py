"""
Test the optimized performance improvements
"""
import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.smart_agent import SmartAgent
from core.memory import MemoryManager
from core.database import DatabaseManager

def test_performance_improvements():
    """Test the performance optimizations"""
    print("🚀 Testing Performance Improvements")
    print("=" * 50)
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        start_time = time.time()
        
        memory = MemoryManager()
        db = DatabaseManager()
        agent = SmartAgent(db, memory)
        
        init_time = time.time() - start_time
        print(f"✅ Initialization completed in {init_time:.2f} seconds")
        
        user_id = "performance_test_user"
        
        # Test 1: Simple conversation (should be fast)
        print("\n📱 Test 1: Simple conversation response time")
        start_time = time.time()
        response1 = agent.process_message(user_id, "Hi there!")
        simple_time = time.time() - start_time
        print(f"✅ Simple response: {simple_time:.2f} seconds")
        print(f"Response: {response1[:100]}...")
        
        # Test 2: Memory-heavy conversation (optimized)
        print("\n🧠 Test 2: Memory-dependent conversation")
        start_time = time.time()
        response2 = agent.process_message(user_id, "Remember what we talked about before regarding my goals and dreams?")
        memory_time = time.time() - start_time
        print(f"✅ Memory response: {memory_time:.2f} seconds")
        print(f"Response: {response2[:100]}...")
        
        # Test 3: Vision board intent detection (fast)
        print("\n🎨 Test 3: Vision board flow detection")
        start_time = time.time()
        response3 = agent.process_message(user_id, "I want to create a vision board for my future")
        vision_time = time.time() - start_time
        print(f"✅ Vision board intent: {vision_time:.2f} seconds")
        print(f"Response: {response3[:100]}...")
        
        # Test 4: Confirmation handling (fast)
        print("\n✅ Test 4: Confirmation processing")
        start_time = time.time()
        response4 = agent.process_message(user_id, "yes go ahead")
        confirm_time = time.time() - start_time
        print(f"✅ Confirmation response: {confirm_time:.2f} seconds")
        print(f"Response: {response4[:100]}...")
        
        # Test 5: Database operations (optimized)
        print("\n💾 Test 5: Database operation speed")
        start_time = time.time()
        response5 = agent.process_message(user_id, "I want to create a habit to exercise daily")
        db_time = time.time() - start_time
        print(f"✅ Database operation: {db_time:.2f} seconds")
        print(f"Response: {response5[:100]}...")
        
        # Performance Summary
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"🔧 Initialization: {init_time:.2f}s")
        print(f"📱 Simple Response: {simple_time:.2f}s")
        print(f"🧠 Memory Response: {memory_time:.2f}s")
        print(f"🎨 Vision Board: {vision_time:.2f}s")
        print(f"✅ Confirmation: {confirm_time:.2f}s")
        print(f"💾 Database Op: {db_time:.2f}s")
        
        avg_response_time = (simple_time + memory_time + vision_time + confirm_time + db_time) / 5
        print(f"\n⚡ Average Response Time: {avg_response_time:.2f}s")
        
        if avg_response_time < 3.0:
            print("🎉 EXCELLENT PERFORMANCE! Average under 3 seconds.")
        elif avg_response_time < 5.0:
            print("✅ GOOD PERFORMANCE! Average under 5 seconds.")
        else:
            print("⚠️ Performance could be improved.")
        
        # Test caching effectiveness
        print("\n🔄 Testing Cache Effectiveness")
        start_time = time.time()
        cached_response = agent.process_message(user_id, "How are you doing?")
        cached_time = time.time() - start_time
        print(f"✅ Cached operation: {cached_time:.2f}s")
        
        if cached_time < simple_time * 0.8:
            print("🚀 Cache is working effectively!")
        else:
            print("📝 Cache may need optimization.")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_performance_improvements()
    if success:
        print("\n🎊 PERFORMANCE TEST COMPLETED!")
    else:
        print("\n⚠️ Performance test had issues.")
