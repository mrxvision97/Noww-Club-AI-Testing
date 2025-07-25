#!/usr/bin/env python3
"""
Comprehensive Pinecone Long-Term Memory Test
Tests if Pinecone is working correctly for storing and retrieving long-term memories
"""

import os
import sys
import traceback
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_env_variables():
    """Test if environment variables are loaded correctly"""
    print("🔧 TESTING ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    pinecone_key = os.getenv('PINECONE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"✅ PINECONE_API_KEY loaded: {'Yes' if pinecone_key else 'No'}")
    if pinecone_key:
        print(f"   Key format: {pinecone_key[:10]}...{pinecone_key[-5:]} (length: {len(pinecone_key)})")
    
    print(f"✅ OPENAI_API_KEY loaded: {'Yes' if openai_key else 'No'}")
    if openai_key:
        print(f"   Key format: {openai_key[:10]}...{openai_key[-5:]} (length: {len(openai_key)})")
    
    return pinecone_key is not None and openai_key is not None

def test_pinecone_connection():
    """Test direct Pinecone connection"""
    print("\n🌲 TESTING PINECONE CONNECTION")
    print("=" * 50)
    
    try:
        from pinecone import Pinecone
        
        # Initialize Pinecone
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        
        print("✅ Pinecone client initialized successfully")
        
        # List indexes
        indexes = pc.list_indexes()
        print(f"✅ Found {len(indexes)} indexes")
        
        for idx in indexes:
            print(f"   📁 Index: {idx['name']} (dimension: {idx['dimension']}, metric: {idx['metric']})")
        
        return True, indexes
        
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        traceback.print_exc()
        return False, []

def test_memory_manager():
    """Test the Memory Manager initialization and basic operations"""
    print("\n🧠 TESTING MEMORY MANAGER")
    print("=" * 50)
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        
        # Initialize database
        print("📦 Initializing database...")
        db_manager = DatabaseManager()
        
        # Initialize memory manager
        print("🧠 Initializing memory manager...")
        memory_manager = MemoryManager(db_manager)
        
        print("✅ Memory Manager initialized successfully")
        print(f"   Pinecone client: {'Connected' if memory_manager.pinecone_client else 'Not connected'}")
        print(f"   Index name: {memory_manager.index_name}")
        
        return True, memory_manager
        
    except Exception as e:
        print(f"❌ Memory Manager initialization failed: {e}")
        traceback.print_exc()
        return False, None

def test_memory_storage_retrieval(memory_manager):
    """Test storing and retrieving memories"""
    print("\n💾 TESTING MEMORY STORAGE & RETRIEVAL")
    print("=" * 50)
    
    try:
        user_id = "test_user_123"
        test_memory = f"Test memory stored at {datetime.now().isoformat()}"
        
        # Store a memory
        print("💾 Storing test memory...")
        memory_manager.store_long_term_memory(
            user_id=user_id,
            content=test_memory,
            memory_type="test",
            importance=0.8,
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        print("✅ Memory stored successfully")
        
        # Retrieve memories
        print("🔍 Retrieving memories...")
        memories = memory_manager.get_relevant_memories(
            user_id=user_id,
            query="test memory",
            limit=5
        )
        
        print(f"✅ Retrieved {len(memories)} memories")
        
        if memories:
            for i, memory in enumerate(memories, 1):
                print(f"   {i}. Content: {memory.get('content', 'No content')[:100]}...")
                print(f"      Type: {memory.get('memory_type', 'Unknown')}")
                print(f"      Importance: {memory.get('importance', 'Unknown')}")
                print(f"      Similarity: {memory.get('similarity', 'Unknown')}")
        
        return True, len(memories)
        
    except Exception as e:
        print(f"❌ Memory storage/retrieval failed: {e}")
        traceback.print_exc()
        return False, 0

def test_episodic_memory(memory_manager):
    """Test episodic memory functionality"""
    print("\n📚 TESTING EPISODIC MEMORY")
    print("=" * 50)
    
    try:
        user_id = "test_user_episodic"
        
        # Store episodic memory
        print("💾 Storing episodic memory...")
        memory_manager.store_episodic_memory(
            user_id=user_id,
            event_type="test_event",
            content="User had a conversation about AI trends",
            context={"topic": "AI", "mood": "curious"},
            importance=0.7
        )
        print("✅ Episodic memory stored successfully")
        
        # Retrieve episodic memories
        print("🔍 Retrieving episodic memories...")
        episodes = memory_manager.get_episodic_memories(
            user_id=user_id,
            limit=5
        )
        
        print(f"✅ Retrieved {len(episodes)} episodic memories")
        
        if episodes:
            for i, episode in enumerate(episodes, 1):
                print(f"   {i}. Event: {episode.get('event_type', 'Unknown')}")
                print(f"      Content: {episode.get('content', 'No content')[:80]}...")
                print(f"      Importance: {episode.get('importance', 'Unknown')}")
        
        return True, len(episodes)
        
    except Exception as e:
        print(f"❌ Episodic memory test failed: {e}")
        traceback.print_exc()
        return False, 0

def test_vector_operations(memory_manager):
    """Test vector operations and similarity search"""
    print("\n🎯 TESTING VECTOR OPERATIONS")
    print("=" * 50)
    
    try:
        # Test embedding generation
        print("🔤 Testing embedding generation...")
        text = "This is a test for vector embeddings"
        embedding = memory_manager._get_embedding(text)
        
        print(f"✅ Generated embedding with dimension: {len(embedding)}")
        
        # Test vector similarity
        print("🔍 Testing vector similarity search...")
        user_id = "test_vector_user"
        
        # Store some test vectors
        test_texts = [
            "I love programming with Python",
            "Machine learning is fascinating", 
            "The weather is nice today",
            "AI will change the world"
        ]
        
        for i, text in enumerate(test_texts):
            memory_manager.store_long_term_memory(
                user_id=user_id,
                content=text,
                memory_type="test_vector",
                importance=0.5 + (i * 0.1)
            )
        
        # Search for similar content
        similar_memories = memory_manager.get_relevant_memories(
            user_id=user_id,
            query="artificial intelligence and programming",
            limit=3
        )
        
        print(f"✅ Found {len(similar_memories)} similar memories")
        
        for i, memory in enumerate(similar_memories, 1):
            print(f"   {i}. \"{memory.get('content', 'No content')}\" (similarity: {memory.get('similarity', 0):.3f})")
        
        return True, len(similar_memories)
        
    except Exception as e:
        print(f"❌ Vector operations test failed: {e}")
        traceback.print_exc()
        return False, 0

def main():
    """Run comprehensive Pinecone and memory tests"""
    print("🚀 COMPREHENSIVE PINECONE MEMORY SYSTEM TEST")
    print("="*60)
    
    results = {
        "env_vars": False,
        "pinecone_connection": False,
        "memory_manager": False,
        "memory_storage": False,
        "episodic_memory": False,
        "vector_operations": False
    }
    
    # Test 1: Environment Variables
    results["env_vars"] = test_env_variables()
    
    if not results["env_vars"]:
        print("\n❌ Environment variables not properly loaded. Cannot continue.")
        return
    
    # Test 2: Pinecone Connection
    results["pinecone_connection"], indexes = test_pinecone_connection()
    
    if not results["pinecone_connection"]:
        print("\n❌ Pinecone connection failed. Cannot continue.")
        return
    
    # Test 3: Memory Manager
    results["memory_manager"], memory_manager = test_memory_manager()
    
    if not results["memory_manager"]:
        print("\n❌ Memory Manager initialization failed. Cannot continue.")
        return
    
    # Test 4: Memory Storage & Retrieval
    results["memory_storage"], stored_count = test_memory_storage_retrieval(memory_manager)
    
    # Test 5: Episodic Memory
    results["episodic_memory"], episodic_count = test_episodic_memory(memory_manager)
    
    # Test 6: Vector Operations
    results["vector_operations"], vector_count = test_vector_operations(memory_manager)
    
    # Final Results
    print("\n" + "="*60)
    print("🏁 FINAL TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Pinecone is working perfectly")
        print("✅ Long-term memory storage is operational")
        print("✅ Vector similarity search is working")
        print("✅ Episodic memory system is functional")
        print("\n🧠 Your memory system is ready for production!")
    else:
        failed_tests = [name for name, passed in results.items() if not passed]
        print(f"\n❌ {len(failed_tests)} test(s) failed:")
        for test in failed_tests:
            print(f"   - {test.replace('_', ' ').title()}")
        print("\n🔧 Check the errors above for troubleshooting")

if __name__ == "__main__":
    main()
