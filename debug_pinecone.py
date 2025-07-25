#!/usr/bin/env python3
"""
Debug script for Pinecone memory storage
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from core.memory import PineconeMemoryStore


def debug_pinecone_storage():
    """Debug Pinecone storage and retrieval"""
    print("🔍 Debugging Pinecone Memory Storage")
    print("=" * 50)
    
    try:
        # Initialize Pinecone store
        pinecone_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_key:
            print("❌ PINECONE_API_KEY not found in environment")
            return False
        
        store = PineconeMemoryStore(
            api_key=pinecone_key.strip('"'),
            index_name="nowwclubchatbot"
        )
        
        test_user_id = "debug_user"
        
        # Test 1: Store a memory
        print("\n1. Testing memory storage...")
        memory_text = "User talked about feeling anxious and starting journaling for emotional processing."
        memory_metadata = {
            'importance': 0.8,
            'human_message': "I've been feeling anxious lately and started journaling to help process my emotions.",
            'ai_message': "That's a wonderful step toward self-care. Journaling can be incredibly powerful for emotional processing and gaining clarity about your feelings.",
            'conversation_type': 'chat'
        }
        
        memory_id = store.store_memory(test_user_id, memory_text, memory_metadata)
        print(f"Stored memory with ID: {memory_id}")
        
        # Test 2: Wait a moment and then search
        import time
        print("\n2. Waiting 2 seconds for indexing...")
        time.sleep(2)
        
        # Test 3: Search for the memory
        print("\n3. Testing memory search...")
        search_results = store.search_memories(test_user_id, "anxious journaling", top_k=5)
        print(f"Found {len(search_results)} memories:")
        for i, result in enumerate(search_results):
            print(f"   {i+1}. Score: {result['score']:.3f}")
            print(f"      Text: {result['text'][:100]}...")
            print(f"      Metadata keys: {list(result['metadata'].keys())}")
        
        # Test 4: Check index stats
        print("\n4. Testing memory statistics...")
        stats = store.get_memory_stats(test_user_id)
        print("Memory Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test 5: Try a different search query
        print("\n5. Testing with different search query...")
        search_results2 = store.search_memories(test_user_id, "emotional processing", top_k=5)
        print(f"Found {len(search_results2)} memories for 'emotional processing':")
        for i, result in enumerate(search_results2):
            print(f"   {i+1}. Score: {result['score']:.3f}")
            print(f"      Text: {result['text'][:100]}...")
        
        # Test 6: Store another memory to test accumulation
        print("\n6. Storing second memory...")
        memory_text2 = "User discussed establishing morning routine with meditation and exercise for stability."
        memory_metadata2 = {
            'importance': 0.7,
            'human_message': "I'm also trying to establish a morning routine with meditation and light exercise.",
            'ai_message': "Building a consistent morning routine is excellent for creating stability and setting positive intentions for your day.",
            'conversation_type': 'chat'
        }
        
        memory_id2 = store.store_memory(test_user_id, memory_text2, memory_metadata2)
        print(f"Stored second memory with ID: {memory_id2}")
        
        # Wait and search again
        time.sleep(2)
        print("\n7. Searching after second memory...")
        search_results3 = store.search_memories(test_user_id, "morning routine", top_k=5)
        print(f"Found {len(search_results3)} memories for 'morning routine':")
        for i, result in enumerate(search_results3):
            print(f"   {i+1}. Score: {result['score']:.3f}")
            print(f"      Text: {result['text'][:100]}...")
        
        # Final stats
        final_stats = store.get_memory_stats(test_user_id)
        print(f"\n8. Final memory count: {final_stats.get('total_memories', 0)}")
        
        # Cleanup
        print("\n9. Cleaning up test memories...")
        store.delete_user_memories(test_user_id)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Pinecone Debug Session")
    print(f"⏰ Debug started at: {datetime.now()}")
    
    success = debug_pinecone_storage()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Debug completed successfully!")
    else:
        print("❌ Debug failed. Check error messages above.")
    
    print(f"⏰ Debug completed at: {datetime.now()}")
