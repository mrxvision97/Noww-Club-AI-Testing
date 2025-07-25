#!/usr/bin/env python3
"""
Test script for the enhanced memory system with Pinecone integration
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from core.memory import MemoryManager
from core.database import DatabaseManager


def test_memory_system():
    """Test the enhanced memory system"""
    print("🧠 Testing Enhanced Memory System with Pinecone Integration")
    print("=" * 60)
    
    try:
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        
        # Test user
        test_user_id = "test_user_enhanced"
        
        print(f"\n✅ Memory system initialized successfully")
        print(f"📊 Testing with user: {test_user_id}")
        
        # Test 1: Basic interaction
        print("\n1. Testing basic interaction...")
        memory_manager.add_interaction(
            test_user_id,
            "I've been feeling anxious lately and started journaling to help process my emotions.",
            "That's a wonderful step toward self-care. Journaling can be incredibly powerful for emotional processing and gaining clarity about your feelings."
        )
        
        # Test 2: Another interaction to trigger episodic memory
        print("2. Adding more interactions...")
        memory_manager.add_interaction(
            test_user_id,
            "I'm also trying to establish a morning routine with meditation and light exercise.",
            "Building a consistent morning routine is excellent for creating stability and setting positive intentions for your day. How has this been feeling for you so far?"
        )
        
        # Test 3: Third interaction to trigger episodic capture
        print("3. Adding third interaction to trigger episodic memory...")
        memory_manager.add_interaction(
            test_user_id,
            "It feels like I'm finally taking control of my life and making positive changes.",
            "It sounds like you're experiencing a powerful transformation. This sense of empowerment and intentional change is beautiful to witness."
        )
        
        # Test 4: Search semantic memories
        print("\n4. Testing semantic memory search...")
        search_results = memory_manager.search_semantic_memories(
            test_user_id, 
            "journaling and anxiety",
            limit=3
        )
        
        print(f"Found {len(search_results)} semantic memories:")
        for i, result in enumerate(search_results):
            print(f"   {i+1}. Score: {result['score']:.3f}")
            print(f"      Text: {result['text'][:100]}...")
        
        # Test 5: Get conversation context
        print("\n5. Testing conversation context generation...")
        context = memory_manager.get_context_for_conversation(
            test_user_id,
            "How can I maintain these positive habits?"
        )
        print(f"Context length: {len(context)} characters")
        print("Context preview:")
        print(context[:300] + "..." if len(context) > 300 else context)
        
        # Test 6: Generate vision story card
        print("\n6. Testing vision story card generation...")
        vision_card = memory_manager.generate_vision_story_card(test_user_id)
        print("Vision Story Card:")
        for key, value in vision_card.items():
            print(f"   {key}: {value}")
        
        # Test 7: Get reflection prompts
        print("\n7. Testing reflection prompts...")
        prompts = memory_manager.get_reflection_prompts(test_user_id)
        print("Reflection prompts:")
        for i, prompt in enumerate(prompts):
            print(f"   {i+1}. {prompt}")
        
        # Test 8: Memory statistics
        print("\n8. Testing memory statistics...")
        stats = memory_manager.get_memory_stats(test_user_id)
        print("Memory Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test 9: Export user data
        print("\n9. Testing data export...")
        exported_data = memory_manager.export_user_data(test_user_id)
        print(f"Exported data contains {len(exported_data)} fields")
        print("Export fields:", list(exported_data.keys()))
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Summary:")
        print(f"   - Semantic memories stored in Pinecone: {stats.get('semantic_memories', 0)}")
        print(f"   - Episodic memories captured: {stats.get('episodic_memories', 0)}")
        print(f"   - Total conversations: {stats.get('total_conversations', 0)}")
        print(f"   - Vision card generated: {'Yes' if vision_card else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_episodic_framework_standalone():
    """Test the episodic memory framework separately"""
    print("\n🧩 Testing Episodic Memory Framework")
    print("=" * 40)
    
    try:
        from core.memory import EpisodicMemoryFramework
        from langchain_openai import ChatOpenAI
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize framework
        framework = EpisodicMemoryFramework(llm)
        
        # Test episodic extraction
        user_message = "I've been focusing on my self-care routine and feeling more confident about my life direction. Starting fresh feels amazing."
        ai_response = "It's wonderful to hear about your renewed sense of direction and the confidence you're building through self-care."
        
        episodic_data = framework.extract_episodic_data(user_message, ai_response)
        
        print("Extracted episodic data:")
        for key, value in episodic_data.items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing episodic framework: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Enhanced Memory System Tests")
    print(f"⏰ Test started at: {datetime.now()}")
    
    # Test episodic framework first
    framework_success = test_episodic_framework_standalone()
    
    # Test full memory system
    memory_success = test_memory_system()
    
    print("\n" + "=" * 60)
    print("🏁 Test Results:")
    print(f"   Episodic Framework: {'✅ PASS' if framework_success else '❌ FAIL'}")
    print(f"   Memory System: {'✅ PASS' if memory_success else '❌ FAIL'}")
    
    if framework_success and memory_success:
        print("\n🎉 All tests passed! Memory system is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    print(f"⏰ Test completed at: {datetime.now()}")
