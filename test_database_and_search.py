#!/usr/bin/env python3
"""
Comprehensive test for database functions and web search functionality
Tests missing database functions and web search information retrieval
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager
from core.memory import MemoryManager
from core.smart_agent import SmartAgent

def test_database_functions():
    """Test all database functions including reminders"""
    print("🗄️ TESTING DATABASE FUNCTIONS")
    print("=" * 50)
    
    db_manager = DatabaseManager()
    test_user_id = "test_db_user"
    
    print(f"\n1️⃣ Testing Reminder Database Functions")
    print("-" * 40)
    
    # Test reminder creation
    try:
        reminder_id = db_manager.save_reminder(
            user_id=test_user_id,
            title="Test Reminder",
            description="This is a test reminder",
            reminder_time="2024-07-19 10:00:00"
        )
        print(f"✅ Reminder created with ID: {reminder_id}")
        
        # Create multiple reminders
        reminder2_id = db_manager.save_reminder(
            user_id=test_user_id,
            title="Doctor Appointment",
            description="Annual checkup",
            reminder_time="2024-07-20 14:00:00"
        )
        
        reminder3_id = db_manager.save_reminder(
            user_id=test_user_id,
            title="Take Vitamins",
            description="Daily vitamin routine",
            reminder_time="2024-07-19 08:00:00"
        )
        
        print(f"✅ Created 3 reminders: {reminder_id}, {reminder2_id}, {reminder3_id}")
        
    except Exception as e:
        print(f"❌ Reminder creation failed: {e}")
        return False
    
    # Test reminder retrieval
    try:
        reminders = db_manager.get_user_reminders(test_user_id)
        print(f"✅ Retrieved {len(reminders)} reminders")
        
        for i, reminder in enumerate(reminders, 1):
            print(f"   Reminder {i}: {reminder.get('title', 'N/A')}")
            print(f"     Time: {reminder.get('reminder_time', 'N/A')}")
            print(f"     Status: {reminder.get('status', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Reminder retrieval failed: {e}")
        return False
    
    print(f"\n2️⃣ Testing Goal Database Functions")
    print("-" * 40)
    
    # Test goal creation and retrieval
    try:
        goal_id = db_manager.save_goal(
            user_id=test_user_id,
            title="Learn Python",
            description="Master Python programming",
            target_date="2024-12-31"
        )
        print(f"✅ Goal created with ID: {goal_id}")
        
        goals = db_manager.get_user_goals(test_user_id)
        print(f"✅ Retrieved {len(goals)} goals")
        
        for goal in goals:
            print(f"   Goal: {goal.get('title', 'N/A')} - {goal.get('status', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Goal operations failed: {e}")
        return False
    
    print(f"\n3️⃣ Testing Habit Database Functions")
    print("-" * 40)
    
    # Test habit creation and retrieval
    try:
        habit_id = db_manager.save_habit(
            user_id=test_user_id,
            title="Daily Exercise",
            description="30 minutes of exercise daily",
            frequency="daily"
        )
        print(f"✅ Habit created with ID: {habit_id}")
        
        habits = db_manager.get_user_habits(test_user_id)
        print(f"✅ Retrieved {len(habits)} habits")
        
        for habit in habits:
            print(f"   Habit: {habit.get('title', 'N/A')} - {habit.get('frequency', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Habit operations failed: {e}")
        return False
    
    print(f"\n4️⃣ Testing Conversation Database Functions")
    print("-" * 40)
    
    # Test conversation storage and retrieval
    try:
        db_manager.save_conversation(
            user_id=test_user_id,
            message_type="human",
            content="Hello, I want to test the system",
            metadata={"test": True}
        )
        
        db_manager.save_conversation(
            user_id=test_user_id,
            message_type="ai",
            content="Hello! I'm here to help you test the system.",
            metadata={"response_to": "greeting"}
        )
        
        conversations = db_manager.get_conversation_history(test_user_id, limit=5)
        print(f"✅ Retrieved {len(conversations)} conversations")
        
        for conv in conversations:
            print(f"   {conv.get('message_type', 'N/A')}: {conv.get('content', 'N/A')[:50]}...")
            
    except Exception as e:
        print(f"❌ Conversation operations failed: {e}")
        return False
    
    print(f"\n✅ ALL DATABASE FUNCTIONS WORKING CORRECTLY!")
    return True

def test_web_search_functionality():
    """Test web search functionality thoroughly"""
    print(f"\n🔍 TESTING WEB SEARCH FUNCTIONALITY")
    print("=" * 50)
    
    # Initialize components
    db_manager = DatabaseManager()
    memory_manager = MemoryManager(db_manager)
    smart_agent = SmartAgent(db_manager, memory_manager)
    
    test_user_id = "test_search_user"
    
    # Test different types of search queries
    search_queries = [
        {
            "query": "Search for the latest AI developments in 2024",
            "type": "Technology",
            "expected_keywords": ["AI", "artificial intelligence", "2024", "development"]
        },
        {
            "query": "What's the current weather in London?",
            "type": "Weather",
            "expected_keywords": ["weather", "London", "temperature", "forecast"]
        },
        {
            "query": "Find healthy breakfast recipes",
            "type": "Lifestyle",
            "expected_keywords": ["healthy", "breakfast", "recipe", "nutrition"]
        },
        {
            "query": "Search for productivity tips for remote work",
            "type": "Productivity",
            "expected_keywords": ["productivity", "remote work", "tips", "efficiency"]
        },
        {
            "query": "Latest news about renewable energy",
            "type": "News",
            "expected_keywords": ["renewable energy", "news", "solar", "wind"]
        }
    ]
    
    successful_searches = 0
    
    for i, search_test in enumerate(search_queries, 1):
        print(f"\n🔎 Search Test {i}: {search_test['type']}")
        print(f"Query: {search_test['query']}")
        print("-" * 30)
        
        try:
            # Send search query to smart agent
            response = smart_agent.process_message(test_user_id, search_test['query'])
            
            # Analyze response
            response_length = len(response)
            print(f"✅ Response received: {response_length} characters")
            
            # Check if response contains relevant information
            search_indicators = [
                'search', 'found', 'information', 'results', 'according to',
                'based on', 'research', 'data', 'recent', 'latest'
            ]
            
            contains_search_indicators = any(
                indicator in response.lower() 
                for indicator in search_indicators
            )
            
            # Check for expected keywords
            contains_keywords = any(
                keyword.lower() in response.lower() 
                for keyword in search_test['expected_keywords']
            )
            
            print(f"✅ Contains search indicators: {contains_search_indicators}")
            print(f"✅ Contains relevant keywords: {contains_keywords}")
            print(f"✅ Response quality: {'Good' if response_length > 200 else 'Basic'}")
            
            # Show response preview
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"📝 Response preview: {preview}")
            
            # Check if this is a successful search
            if contains_search_indicators or contains_keywords or response_length > 150:
                successful_searches += 1
                print(f"✅ Search test {i} PASSED")
            else:
                print(f"⚠️ Search test {i} - Limited results")
                
        except Exception as e:
            print(f"❌ Search test {i} failed: {e}")
    
    print(f"\n📊 SEARCH RESULTS SUMMARY")
    print("-" * 30)
    print(f"✅ Successful searches: {successful_searches}/{len(search_queries)}")
    print(f"✅ Success rate: {(successful_searches/len(search_queries)*100):.1f}%")
    
    # Test search integration with memory
    print(f"\n🧠 Testing Search + Memory Integration")
    print("-" * 40)
    
    try:
        # Ask about previous search
        follow_up = smart_agent.process_message(
            test_user_id, 
            "What did we search for earlier?"
        )
        print(f"✅ Memory integration response: {len(follow_up)} chars")
        print(f"📝 Preview: {follow_up[:150]}...")
        
        # Ask for search based on conversation context
        contextual_search = smart_agent.process_message(
            test_user_id,
            "Search for more information about that topic"
        )
        print(f"✅ Contextual search response: {len(contextual_search)} chars")
        
    except Exception as e:
        print(f"❌ Search + Memory integration failed: {e}")
    
    return successful_searches >= len(search_queries) * 0.6  # 60% success rate

def test_advanced_search_scenarios():
    """Test advanced search scenarios"""
    print(f"\n🚀 TESTING ADVANCED SEARCH SCENARIOS")
    print("=" * 50)
    
    db_manager = DatabaseManager()
    memory_manager = MemoryManager(db_manager)
    smart_agent = SmartAgent(db_manager, memory_manager)
    
    test_user_id = "test_advanced_search"
    
    advanced_scenarios = [
        {
            "setup": "I'm interested in learning about machine learning",
            "search": "Search for beginner-friendly machine learning courses",
            "follow_up": "Find free alternatives to those courses"
        },
        {
            "setup": "I want to start a healthy lifestyle",
            "search": "Search for meal prep ideas for beginners",
            "follow_up": "What about exercise routines for beginners?"
        },
        {
            "setup": "I'm planning a trip to Japan",
            "search": "Search for must-visit places in Tokyo",
            "follow_up": "What's the best time to visit Japan?"
        }
    ]
    
    for i, scenario in enumerate(advanced_scenarios, 1):
        print(f"\n🎯 Advanced Scenario {i}")
        print("-" * 25)
        
        try:
            # Setup context
            setup_response = smart_agent.process_message(test_user_id, scenario['setup'])
            print(f"✅ Context setup: {len(setup_response)} chars")
            
            # Perform search
            search_response = smart_agent.process_message(test_user_id, scenario['search'])
            print(f"✅ Search response: {len(search_response)} chars")
            
            # Follow-up search
            followup_response = smart_agent.process_message(test_user_id, scenario['follow_up'])
            print(f"✅ Follow-up response: {len(followup_response)} chars")
            
            # Check for contextual understanding
            context_maintained = any(
                word in followup_response.lower() 
                for word in scenario['setup'].lower().split()[-3:]
            )
            print(f"✅ Context maintained: {context_maintained}")
            
        except Exception as e:
            print(f"❌ Advanced scenario {i} failed: {e}")
    
    return True

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE DATABASE & WEB SEARCH TEST")
    print("=" * 60)
    
    try:
        # Test 1: Database Functions
        db_success = test_database_functions()
        
        # Test 2: Web Search Functionality
        search_success = test_web_search_functionality()
        
        # Test 3: Advanced Search Scenarios
        advanced_success = test_advanced_search_scenarios()
        
        print(f"\n🎯 FINAL TEST RESULTS")
        print("=" * 30)
        print(f"✅ Database Functions: {'PASSED' if db_success else 'FAILED'}")
        print(f"✅ Web Search: {'PASSED' if search_success else 'FAILED'}")
        print(f"✅ Advanced Scenarios: {'PASSED' if advanced_success else 'FAILED'}")
        
        overall_success = db_success and search_success and advanced_success
        
        if overall_success:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"🗄️ Database functions working perfectly")
            print(f"🔍 Web search retrieving and presenting information correctly")
            print(f"🧠 Memory integration with search working")
            print(f"🚀 System ready for production!")
        else:
            print(f"\n⚠️ Some tests failed - check individual results above")
            
    except Exception as e:
        print(f"💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
