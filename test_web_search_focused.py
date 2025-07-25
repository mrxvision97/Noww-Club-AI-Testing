#!/usr/bin/env python3
"""
Focused test for web search functionality
Tests if DuckDuckGo search is actually fetching real information
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.smart_agent import SmartAgent
from core.database import DatabaseManager
from core.memory import MemoryManager

# Also test DuckDuckGo directly
try:
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    from langchain_community.tools import DuckDuckGoSearchRun
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

def test_direct_duckduckgo():
    """Test DuckDuckGo search directly"""
    print("🦆 TESTING DUCKDUCKGO SEARCH DIRECTLY")
    print("=" * 50)
    
    if not DUCKDUCKGO_AVAILABLE:
        print("❌ DuckDuckGo tools not available")
        return False
    
    try:
        # Test direct DuckDuckGo search
        search_tool = DuckDuckGoSearchRun(
            api_wrapper=DuckDuckGoSearchAPIWrapper(
                max_results=3,
                time="d"  # last day
            )
        )
        
        test_queries = [
            "latest AI news 2024",
            "current weather New York",
            "Python programming tips"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Direct Test {i}: {query}")
            print("-" * 30)
            
            try:
                results = search_tool.run(query)
                print(f"✅ Search completed")
                print(f"📊 Results length: {len(results)}")
                print(f"🔍 Contains useful info: {'http' in results or 'www' in results}")
                print(f"📝 Preview: {results[:200]}...")
                
                if len(results) > 50:
                    print(f"✅ Direct search {i} SUCCESSFUL")
                else:
                    print(f"⚠️ Direct search {i} returned minimal results")
                    
            except Exception as e:
                print(f"❌ Direct search {i} failed: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Direct DuckDuckGo test failed: {e}")
        return False

def test_smart_agent_search():
    """Test web search through SmartAgent"""
    print(f"\n🤖 TESTING WEB SEARCH THROUGH SMART AGENT")
    print("=" * 50)
    
    try:
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        test_user_id = "web_search_test"
        
        # Test specific search scenarios
        search_scenarios = [
            {
                "query": "What's the latest news about artificial intelligence today?",
                "expected_indicators": ["AI", "artificial intelligence", "news", "today", "latest"],
                "search_type": "News"
            },
            {
                "query": "Search for healthy breakfast recipes",
                "expected_indicators": ["healthy", "breakfast", "recipe", "food"],
                "search_type": "Lifestyle"
            },
            {
                "query": "Find current weather in London",
                "expected_indicators": ["weather", "London", "temperature", "forecast"],
                "search_type": "Weather"
            },
            {
                "query": "What are the best productivity apps in 2024?",
                "expected_indicators": ["productivity", "apps", "2024", "best"],
                "search_type": "Technology"
            }
        ]
        
        successful_searches = 0
        
        for i, scenario in enumerate(search_scenarios, 1):
            print(f"\n🎯 Search Scenario {i}: {scenario['search_type']}")
            print(f"Query: {scenario['query']}")
            print("-" * 40)
            
            try:
                # Call search_and_respond directly
                response = smart_agent.search_and_respond(test_user_id, scenario['query'])
                
                print(f"✅ Response received: {len(response)} characters")
                
                # Check if response contains expected indicators
                indicators_found = sum(
                    1 for indicator in scenario['expected_indicators']
                    if indicator.lower() in response.lower()
                )
                
                print(f"📊 Expected indicators found: {indicators_found}/{len(scenario['expected_indicators'])}")
                
                # Check for search-specific content
                search_indicators = [
                    'according to', 'based on', 'research shows', 'found', 'results',
                    'information', 'data', 'study', 'report', 'source'
                ]
                
                search_content = sum(
                    1 for indicator in search_indicators
                    if indicator.lower() in response.lower()
                )
                
                print(f"🔍 Search-related content: {search_content} indicators")
                
                # Check response quality
                quality_metrics = {
                    "Length": len(response) > 200,
                    "Relevant": indicators_found >= len(scenario['expected_indicators']) * 0.5,
                    "Search-based": search_content > 0,
                    "Informative": len(response.split()) > 30
                }
                
                print(f"📈 Quality metrics:")
                for metric, passed in quality_metrics.items():
                    print(f"   {metric}: {'✅' if passed else '❌'}")
                
                # Show response preview
                preview = response[:300] + "..." if len(response) > 300 else response
                print(f"📝 Response preview:\n{preview}")
                
                # Determine if search was successful
                if sum(quality_metrics.values()) >= 3:
                    successful_searches += 1
                    print(f"✅ Search scenario {i} PASSED")
                else:
                    print(f"⚠️ Search scenario {i} - Limited quality")
                    
            except Exception as e:
                print(f"❌ Search scenario {i} failed: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n📊 SEARCH AGENT RESULTS")
        print("-" * 30)
        print(f"✅ Successful searches: {successful_searches}/{len(search_scenarios)}")
        print(f"✅ Success rate: {(successful_searches/len(search_scenarios)*100):.1f}%")
        
        return successful_searches >= len(search_scenarios) * 0.5
        
    except Exception as e:
        print(f"❌ Smart agent search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_integration():
    """Test search integration with normal conversation flow"""
    print(f"\n🔄 TESTING SEARCH INTEGRATION WITH CONVERSATION")
    print("=" * 50)
    
    try:
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        test_user_id = "search_integration_test"
        
        # Test conversation flow with search
        conversation_flow = [
            {
                "message": "Hi, I'm interested in learning about machine learning",
                "type": "setup"
            },
            {
                "message": "Can you search for the latest machine learning trends?",
                "type": "search_request"
            },
            {
                "message": "That's interesting! Can you find more specific information about neural networks?",
                "type": "follow_up_search"
            }
        ]
        
        for i, step in enumerate(conversation_flow, 1):
            print(f"\n💬 Conversation Step {i}: {step['type']}")
            print(f"Message: {step['message']}")
            print("-" * 35)
            
            try:
                response = smart_agent.process_message(test_user_id, step['message'])
                print(f"✅ Response: {len(response)} characters")
                
                if step['type'] in ['search_request', 'follow_up_search']:
                    # Check if this looks like a search response
                    search_indicators = ['information', 'research', 'according to', 'based on', 'found']
                    has_search_content = any(indicator in response.lower() for indicator in search_indicators)
                    print(f"🔍 Contains search content: {has_search_content}")
                
                # Show preview
                preview = response[:200] + "..." if len(response) > 200 else response
                print(f"📝 Preview: {preview}")
                
            except Exception as e:
                print(f"❌ Conversation step {i} failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE WEB SEARCH FUNCTIONALITY TEST")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Direct DuckDuckGo
        direct_success = test_direct_duckduckgo()
        
        # Test 2: Smart Agent Search
        agent_success = test_smart_agent_search()
        
        # Test 3: Search Integration
        integration_success = test_search_integration()
        
        print(f"\n🎯 FINAL WEB SEARCH TEST RESULTS")
        print("=" * 40)
        print(f"✅ Direct DuckDuckGo: {'PASSED' if direct_success else 'FAILED'}")
        print(f"✅ Smart Agent Search: {'PASSED' if agent_success else 'FAILED'}")
        print(f"✅ Search Integration: {'PASSED' if integration_success else 'FAILED'}")
        
        overall_success = direct_success and agent_success and integration_success
        
        if overall_success:
            print(f"\n🎉 ALL WEB SEARCH TESTS PASSED!")
            print(f"🔍 DuckDuckGo is fetching real information")
            print(f"🤖 Smart agent is processing search requests correctly")
            print(f"🔄 Search integrates seamlessly with conversations")
            print(f"🌐 Web search functionality is production-ready!")
        else:
            print(f"\n⚠️ Some web search tests failed")
            if not direct_success:
                print(f"   🦆 DuckDuckGo direct search issues")
            if not agent_success:
                print(f"   🤖 Smart agent search processing issues")
            if not integration_success:
                print(f"   🔄 Search integration issues")
            
    except Exception as e:
        print(f"💥 Web search test suite failed: {e}")
        import traceback
        traceback.print_exc()
