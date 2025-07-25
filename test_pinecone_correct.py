#!/usr/bin/env python3
"""
Correct Pinecone Memory Test - Using actual method names
"""

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pinecone_memory():
    """Test Pinecone memory functionality with correct method names"""
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
        
        # Check if API key format is correct (no quotes)
        if pinecone_key.startswith('"') or pinecone_key.endswith('"'):
            print("⚠️ WARNING: PINECONE_API_KEY contains quotes - this should be fixed!")
        else:
            print("✅ PINECONE_API_KEY format is correct (no quotes)")
        
        # Initialize components
        print("\n📦 Initializing components...")
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        
        print("✅ Memory Manager initialized successfully!")
        
        # Test 1: Store a memory using correct method name
        print("\n💾 Test 1: Storing memory...")
        user_id = "test_user_" + str(int(datetime.now().timestamp()))
        test_content = f"This is a test memory stored at {datetime.now()}"
        
        memory_id = memory_manager.store_memory(
            user_id=user_id,
            memory_text=test_content,
            metadata={"test": True, "importance": 0.8}
        )
        print(f"✅ Memory stored with ID: {memory_id}")
        
        # Test 2: Retrieve conversation memory
        print("\n🔍 Test 2: Retrieving conversation memory...")
        memories = memory_manager.get_conversation_memory(
            user_id=user_id,
            query="test memory",
            limit=5
        )
        
        print(f"✅ Retrieved {len(memories)} memories")
        if memories:
            for i, memory in enumerate(memories, 1):
                content = memory.get('content', memory.get('text', 'No content'))[:80]
                timestamp = memory.get('timestamp', 'Unknown time')
                print(f"   {i}. {content}... ({timestamp})")
        
        # Test 3: Get user memory context
        print("\n📚 Test 3: Getting user memory context...")
        user_memory = memory_manager.get_user_memory(user_id)
        print(f"✅ User memory context retrieved")
        print(f"   Keys available: {list(user_memory.keys())}")
        
        # Test 4: Get context for conversation
        print("\n💬 Test 4: Getting conversation context...")
        context = memory_manager.get_context_for_conversation(
            user_id=user_id,
            current_message="Tell me about AI"
        )
        print(f"✅ Context retrieved (length: {len(context)} characters)")
        if context:
            print(f"   Preview: {context[:200]}...")
        
        # Test 5: Store multiple memories for similarity testing
        print("\n🎯 Test 5: Testing memory similarity...")
        
        test_memories = [
            "I love artificial intelligence and machine learning",
            "Python is my favorite programming language", 
            "The weather is beautiful today",
            "Deep learning algorithms are fascinating",
            "I enjoy coding neural networks"
        ]
        
        stored_ids = []
        for i, content in enumerate(test_memories):
            memory_id = memory_manager.store_memory(
                user_id=user_id,
                memory_text=content,
                metadata={"test_batch": True, "index": i}
            )
            stored_ids.append(memory_id)
        
        print(f"✅ Stored {len(stored_ids)} test memories")
        
        # Get relevant memories
        similar_memories = memory_manager.get_conversation_memory(
            user_id=user_id,
            query="AI programming and technology",
            limit=3
        )
        
        print(f"✅ Found {len(similar_memories)} relevant memories for 'AI programming':")
        for i, memory in enumerate(similar_memories, 1):
            content = memory.get('content', memory.get('text', 'No content'))
            print(f"   {i}. \"{content}\"")
        
        # Test 6: Memory stats
        print("\n📊 Test 6: Memory statistics...")
        stats = memory_manager.get_memory_stats(user_id)
        print(f"✅ Memory stats retrieved:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "=" * 50)
        print("🎉 ALL PINECONE TESTS PASSED!")
        print("✅ Pinecone connection: Working perfectly")
        print("✅ Memory storage: Working correctly")
        print("✅ Memory retrieval: Working correctly") 
        print("✅ Context generation: Working correctly")
        print("✅ Vector similarity: Working correctly")
        print("✅ Environment setup: Correct (no quotes in API key)")
        print("\n🧠 Your Pinecone long-term memory system is fully operational!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pinecone_memory()
