#!/usr/bin/env python3
"""
Test script for cloud-based Pinecone memory with 1024-dimension embeddings
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from core.memory import MemoryManager, PineconeMemoryStore
from core.database import DatabaseManager


def test_cloud_embeddings():
    """Test the cloud-based embedding system"""
    print("☁️  Testing Cloud-Based Pinecone Memory System")
    print("=" * 60)
    
    try:
        # Check API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        pinecone_key = os.getenv("PINECONE_API_KEY")
        
        if not openai_key:
            print("❌ OPENAI_API_KEY not found")
            return False
        if not pinecone_key:
            print("❌ PINECONE_API_KEY not found")
            return False
        
        print("✅ API keys found")
        
        # Initialize Pinecone store directly
        print("\n1. Initializing Pinecone Memory Store...")
        store = PineconeMemoryStore(
            api_key=pinecone_key.strip('"'),
            index_name="nowwclubchatbot"
        )
        
        test_user_id = "cloud_test_user"
        
        # Test 2: Create and store embeddings
        print("\n2. Testing embedding creation...")
        test_texts = [
            "I've been feeling anxious and started journaling for emotional processing",
            "Building a morning routine with meditation and exercise for stability",
            "Feeling confident about my transformation journey and personal growth"
        ]
        
        stored_memories = []
        for i, text in enumerate(test_texts):
            print(f"   Storing memory {i+1}: {text[:50]}...")
            memory_id = store.store_memory(
                test_user_id,
                text,
                {
                    'importance': 0.8,
                    'test_index': i,
                    'conversation_type': 'test'
                }
            )
            stored_memories.append(memory_id)
            print(f"   ✅ Stored with ID: {memory_id}")
        
        # Test 3: Wait for indexing
        print("\n3. Waiting for Pinecone indexing...")
        time.sleep(3)
        
        # Test 4: Search functionality
        print("\n4. Testing semantic search...")
        search_queries = [
            "anxiety journaling",
            "morning routine meditation",
            "confidence transformation",
            "emotional wellness"
        ]
        
        for query in search_queries:
            print(f"\n   Query: '{query}'")
            results = store.search_memories(test_user_id, query, top_k=3)
            print(f"   Found {len(results)} results:")
            for j, result in enumerate(results):
                print(f"      {j+1}. Score: {result['score']:.3f}")
                print(f"         Text: {result['text'][:80]}...")
        
        # Test 5: Memory statistics
        print("\n5. Checking memory statistics...")
        stats = store.get_memory_stats(test_user_id)
        print(f"   Total memories: {stats.get('total_memories', 0)}")
        print(f"   Namespace: {stats.get('namespace', 'unknown')}")
        
        # Test 6: Full memory manager
        print("\n6. Testing full Memory Manager...")
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        
        # Add interactions
        interactions = [
            ("I want to focus on self-care and building healthy habits", 
             "That's wonderful! Self-care is the foundation of personal growth and well-being."),
            ("I'm in a transformation phase and feeling really empowered", 
             "It sounds like you're embracing positive change. This empowerment will serve you well."),
            ("My journey feels like a fresh start with new possibilities", 
             "Fresh starts bring such beautiful energy. You're creating space for amazing growth.")
        ]
        
        for human_msg, ai_msg in interactions:
            memory_manager.add_interaction(test_user_id, human_msg, ai_msg)
            print(f"   ✅ Added interaction: {human_msg[:40]}...")
        
        # Test 7: Context generation
        print("\n7. Testing context generation...")
        context = memory_manager.get_context_for_conversation(
            test_user_id,
            "How can I maintain my positive momentum?"
        )
        print(f"   Generated context ({len(context)} chars):")
        print(f"   {context[:200]}...")
        
        # Test 8: Vision card generation
        print("\n8. Testing vision card generation...")
        vision_card = memory_manager.generate_vision_story_card(test_user_id)
        print("   Vision Card:")
        for key, value in vision_card.items():
            if key in ['user_id', 'lifestyle_season', 'emotional_theme', 'mood_aesthetic']:
                print(f"      {key}: {value}")
        
        # Test 9: Get memory stats from manager
        print("\n9. Final memory statistics...")
        final_stats = memory_manager.get_memory_stats(test_user_id)
        print("   Memory Stats:")
        for key, value in final_stats.items():
            print(f"      {key}: {value}")
        
        # Cleanup
        print("\n10. Cleaning up test data...")
        store.delete_user_memories(test_user_id)
        memory_manager.clear_user_memory(test_user_id)
        
        print("\n✅ All cloud-based tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embedding_dimensions():
    """Test embedding dimension handling"""
    print("\n🔍 Testing Embedding Dimensions")
    print("=" * 40)
    
    try:
        pinecone_key = os.getenv("PINECONE_API_KEY")
        store = PineconeMemoryStore(
            api_key=pinecone_key.strip('"'),
            index_name="nowwclubchatbot"
        )
        
        # Test embedding creation
        test_text = "This is a test for embedding dimensions"
        embedding = store._create_embedding(test_text)
        
        print(f"Text: '{test_text}'")
        print(f"Embedding dimension: {len(embedding)}")
        print(f"Expected dimension: 1024")
        print(f"First 5 values: {embedding[:5]}")
        print(f"Last 5 values: {embedding[-5:]}")
        
        if len(embedding) == 1024:
            print("✅ Embedding dimension is correct!")
            return True
        else:
            print("❌ Embedding dimension mismatch!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing embeddings: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Cloud-Based Memory System Tests")
    print(f"⏰ Test started at: {datetime.now()}")
    
    # Test embedding dimensions first
    dimension_success = test_embedding_dimensions()
    
    # Test full system
    system_success = test_cloud_embeddings()
    
    print("\n" + "=" * 60)
    print("🏁 Test Results:")
    print(f"   Embedding Dimensions: {'✅ PASS' if dimension_success else '❌ FAIL'}")
    print(f"   Full System: {'✅ PASS' if system_success else '❌ FAIL'}")
    
    if dimension_success and system_success:
        print("\n🎉 All tests passed! Cloud-based memory system is ready!")
        print("📊 Your system is now using:")
        print("   - OpenAI text-embedding-3-large (cloud)")
        print("   - 1024-dimensional vectors (truncated)")
        print("   - Pinecone serverless index")
        print("   - Per-user namespace isolation")
    else:
        print("\n⚠️  Some tests failed. Check error messages above.")
    
    print(f"⏰ Test completed at: {datetime.now()}")
