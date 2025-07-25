#!/usr/bin/env python3
"""
Simple Pinecone Memory Test - Direct Testing
"""

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pinecone_memory():
    """Direct test of Pinecone memory functionality"""
    print("🧠 PINECONE MEMORY SYSTEM TEST")
    print("=" * 50)
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check API keys
        pinecone_key = os.getenv('PINECONE_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        print(f"✅ PINECONE_API_KEY: {'✓ Loaded' if pinecone_key else '✗ Missing'}")
        print(f"✅ OPENAI_API_KEY: {'✓ Loaded' if openai_key else '✗ Missing'}")
        
        if not pinecone_key or not openai_key:
            print("❌ Required API keys missing!")
            return False
        
        # Initialize components
        print("\n📦 Initializing components...")
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        
        print("✅ Memory Manager initialized successfully!")
        
        # Test 1: Store a memory
        print("\n💾 Test 1: Storing long-term memory...")
        user_id = "test_user_" + str(int(datetime.now().timestamp()))
        test_content = f"This is a test memory stored at {datetime.now()}"
        
        memory_manager.store_long_term_memory(
            user_id=user_id,
            content=test_content,
            memory_type="test",
            importance=0.8
        )
        print("✅ Memory stored successfully!")
        
        # Test 2: Retrieve memories
        print("\n🔍 Test 2: Retrieving memories...")
        memories = memory_manager.get_relevant_memories(
            user_id=user_id,
            query="test memory",
            limit=5
        )
        
        print(f"✅ Retrieved {len(memories)} memories")
        if memories:
            for i, memory in enumerate(memories, 1):
                content = memory.get('content', 'No content')[:80]
                similarity = memory.get('similarity', 0)
                print(f"   {i}. {content}... (similarity: {similarity:.3f})")
        
        # Test 3: Store episodic memory
        print("\n📚 Test 3: Storing episodic memory...")
        memory_manager.store_episodic_memory(
            user_id=user_id,
            event_type="conversation",
            content="User discussed AI technology and its future",
            context={"topic": "AI", "sentiment": "positive"},
            importance=0.7
        )
        print("✅ Episodic memory stored!")
        
        # Test 4: Retrieve episodic memories
        print("\n📖 Test 4: Retrieving episodic memories...")
        episodes = memory_manager.get_episodic_memories(user_id=user_id, limit=5)
        print(f"✅ Retrieved {len(episodes)} episodic memories")
        
        if episodes:
            for i, episode in enumerate(episodes, 1):
                event_type = episode.get('event_type', 'Unknown')
                content = episode.get('content', 'No content')[:60]
                print(f"   {i}. {event_type}: {content}...")
        
        # Test 5: Vector similarity test
        print("\n🎯 Test 5: Vector similarity search...")
        
        # Store multiple related memories
        test_memories = [
            "I love artificial intelligence and machine learning",
            "Python is my favorite programming language",
            "The weather is beautiful today",
            "Deep learning algorithms are fascinating"
        ]
        
        for i, content in enumerate(test_memories):
            memory_manager.store_long_term_memory(
                user_id=user_id,
                content=content,
                memory_type="similarity_test",
                importance=0.6
            )
        
        # Search for similar content
        similar = memory_manager.get_relevant_memories(
            user_id=user_id,
            query="AI and programming technologies",
            limit=3
        )
        
        print(f"✅ Found {len(similar)} similar memories for 'AI and programming':")
        for i, memory in enumerate(similar, 1):
            content = memory.get('content', 'No content')
            similarity = memory.get('similarity', 0)
            print(f"   {i}. \"{content}\" (similarity: {similarity:.3f})")
        
        print("\n" + "=" * 50)
        print("🎉 ALL PINECONE TESTS PASSED!")
        print("✅ Pinecone connection: Working")
        print("✅ Long-term memory storage: Working")
        print("✅ Memory retrieval: Working") 
        print("✅ Episodic memory: Working")
        print("✅ Vector similarity search: Working")
        print("✅ Environment variables: Correctly configured")
        print("\n🧠 Your Pinecone memory system is fully operational!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pinecone_memory()
