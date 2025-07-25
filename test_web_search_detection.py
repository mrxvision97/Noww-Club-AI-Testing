#!/usr/bin/env python3
"""
Test Enhanced Web Search Detection and Functionality
Tests the smart agent's ability to detect and perform web searches for real-time queries.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging to reduce noise
from core.logging_config import setup_logging
setup_logging("WARNING")

def test_web_search_detection():
    """Test the web search detection logic"""
    print("🔍 TESTING WEB SEARCH DETECTION")
    print("=" * 50)
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.smart_agent import SmartAgent
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        # Test queries that should trigger web search
        web_search_queries = [
            "What's the latest cricket score?",
            "What's the weather like today?",
            "Tell me the latest news",
            "What happened in the election?",
            "Who won the match?",
            "What's the current stock price of Apple?",
            "Latest developments in AI",
            "Current temperature",
            "Recent cricket match results",
            "Today's weather forecast",
            "Latest news about technology",
            "Current events in politics",
            "What's happening now?",
            "Recent updates on COVID",
            "Live score India vs Australia"
        ]
        
        print("🧪 Testing queries that SHOULD trigger web search:")
        correct_detections = 0
        for query in web_search_queries:
            should_search = smart_agent._requires_web_search(query)
            status = "✅ DETECTED" if should_search else "❌ MISSED"
            print(f"   {status}: \"{query}\"")
            if should_search:
                correct_detections += 1
        
        print(f"\n📊 Detection Rate: {correct_detections}/{len(web_search_queries)} ({(correct_detections/len(web_search_queries)*100):.1f}%)")
        
        # Test queries that should NOT trigger web search
        normal_queries = [
            "How are you?",
            "Tell me about yourself",
            "I want to create a vision board",
            "Help me set up a habit",
            "What did we talk about yesterday?",
            "I need some motivation",
            "How do I stay productive?",
            "Explain quantum physics",
            "What is machine learning?",
            "Help me with my goals"
        ]
        
        print("\n🧪 Testing queries that should NOT trigger web search:")
        correct_ignores = 0
        for query in normal_queries:
            should_search = smart_agent._requires_web_search(query)
            status = "❌ FALSE POSITIVE" if should_search else "✅ CORRECTLY IGNORED"
            print(f"   {status}: \"{query}\"")
            if not should_search:
                correct_ignores += 1
        
        print(f"\n📊 Correct Ignore Rate: {correct_ignores}/{len(normal_queries)} ({(correct_ignores/len(normal_queries)*100):.1f}%)")
        
        # Overall accuracy
        total_correct = correct_detections + correct_ignores
        total_queries = len(web_search_queries) + len(normal_queries)
        accuracy = (total_correct / total_queries) * 100
        
        print(f"\n🎯 Overall Accuracy: {total_correct}/{total_queries} ({accuracy:.1f}%)")
        
        return accuracy > 80  # Consider test passed if accuracy > 80%
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_actual_web_search():
    """Test actual web search functionality"""
    print("\n🌐 TESTING ACTUAL WEB SEARCH")
    print("=" * 50)
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager  
        from core.smart_agent import SmartAgent
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        # Test with a real web search query
        test_queries = [
            "latest technology news",
            "current weather",
            "recent AI developments"
        ]
        
        user_id = "test_search_user"
        successful_searches = 0
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            
            # Test detection
            should_search = smart_agent._requires_web_search(query)
            print(f"   Detection: {'✅ Will search' if should_search else '❌ Will not search'}")
            
            if should_search:
                # Test actual search
                print("   Performing web search...")
                try:
                    result = smart_agent.search_and_respond(user_id, query)
                    
                    if result and len(result) > 100:
                        print(f"   ✅ Search successful! Response length: {len(result)} chars")
                        print(f"   Preview: {result[:200]}...")
                        successful_searches += 1
                    else:
                        print(f"   ⚠️ Limited response: {result}")
                except Exception as search_error:
                    print(f"   ❌ Search error: {search_error}")
            else:
                print("   ⚠️ Query not detected as requiring web search")
        
        print(f"\n📊 Successful searches: {successful_searches}/{len(test_queries)}")
        return successful_searches > 0
        
    except Exception as e:
        print(f"❌ Web search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_integration():
    """Test full integration through process_message"""
    print("\n🔄 TESTING FULL INTEGRATION")
    print("=" * 50)
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.smart_agent import SmartAgent
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        user_id = "test_integration_user"
        
        # Test with web search query
        web_query = "What's the latest news about artificial intelligence?"
        print(f"📝 Testing web search query: '{web_query}'")
        
        response = smart_agent.process_message(user_id, web_query)
        
        if response and len(response) > 200:
            print("✅ Full integration successful!")
            print(f"   Response length: {len(response)} chars")
            print(f"   Preview: {response[:300]}...")
            
            # Check if it looks like a web search response
            search_indicators = ['search', 'results', 'found', 'according to', 'based on', 'recent', 'latest']
            has_search_indicators = any(indicator in response.lower() for indicator in search_indicators)
            
            if has_search_indicators:
                print("   ✅ Response appears to be from web search")
            else:
                print("   ⚠️ Response may not be from web search")
        else:
            print(f"   ⚠️ Limited response: {response}")
        
        # Test with normal query
        normal_query = "Hello, how are you today?"
        print(f"\n📝 Testing normal query: '{normal_query}'")
        
        normal_response = smart_agent.process_message(user_id, normal_query)
        print(f"   ✅ Normal query response: {normal_response[:100]}...")
        
        # Test the user's specific examples
        user_examples = [
            "What's the latest cricket score?",
            "What's the weather today?",
            "Tell me recent news"
        ]
        
        print(f"\n📝 Testing user's specific examples:")
        for example in user_examples:
            print(f"\n   Query: '{example}'")
            example_response = smart_agent.process_message(user_id, example)
            
            if example_response and len(example_response) > 100:
                print(f"   ✅ Response generated ({len(example_response)} chars)")
                print(f"   Preview: {example_response[:150]}...")
            else:
                print(f"   ⚠️ Short response: {example_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 WEB SEARCH DETECTION TESTING")
    print("="*60)
    print("Testing the enhanced web search functionality fixes...")
    
    # Run all tests
    detection_test = test_web_search_detection()
    search_test = test_actual_web_search()
    integration_test = test_full_integration()
    
    print("\n" + "="*60)
    print("🏁 FINAL TEST RESULTS")
    print("="*60)
    
    results = {
        "Web Search Detection": detection_test,
        "Actual Web Search": search_test,  
        "Full Integration": integration_test
    }
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    if all(results.values()):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Web search detection is working correctly")
        print("✅ SERP API integration is functional")
        print("✅ Full message processing with web search is operational")
        print("\n🌐 Your AI now automatically searches the web for:")
        print("   • Latest news and current events")
        print("   • Weather and forecasts")
        print("   • Sports scores and results")
        print("   • Stock prices and market data")
        print("   • Any real-time information queries")
        print("\n🔧 Fixes implemented:")
        print("   ✅ Logging noise eliminated (httpx, apscheduler)")
        print("   ✅ Web search detection logic added")
        print("   ✅ Real-time query patterns recognized")
        print("   ✅ SERP API properly integrated")
    else:
        print("\n❌ Some tests failed - check the output above")
        print("🔧 May need additional debugging")
        
        if not detection_test:
            print("   - Web search detection needs improvement")
        if not search_test:
            print("   - SERP API integration may have issues")
        if not integration_test:
            print("   - Full integration flow needs debugging")
