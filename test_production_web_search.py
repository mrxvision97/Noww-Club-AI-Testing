#!/usr/bin/env python3
"""
Production-Ready Web Search Detection Test
Tests contextual analysis and ambiguous keyword handling for production deployment.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging to reduce noise
from core.logging_config import setup_logging
setup_logging("WARNING")

def test_ambiguous_keyword_handling():
    """Test handling of ambiguous keywords that could be personal or web search"""
    print("🔍 TESTING AMBIGUOUS KEYWORD HANDLING")
    print("=" * 60)
    
    try:
        from core.smart_agent import SmartAgent
        smart_agent = SmartAgent.__new__(SmartAgent)
        
        # Critical test cases - these should NOT trigger web search (personal/conversational)
        personal_queries_with_ambiguous_keywords = [
            # "Today" in personal context
            "How are you doing today?",
            "I'm feeling great today",
            "What should I focus on today?",
            "Help me plan my day today",
            "I have a meeting today",
            "Today has been challenging for me",
            "Can you motivate me today?",
            
            # "Latest" in personal context  
            "What's my latest goal progress?",
            "Show me my latest habits",
            "What was our latest conversation about?",
            "Tell me about my latest achievements",
            
            # "Current" in personal context
            "What's my current mood?",
            "Help with my current situation",
            "What are my current goals?",
            "Check my current habit streak",
            
            # "Recent" in personal context
            "What did we discuss recently?",
            "Show my recent progress",
            "Recent conversation topics",
            "My recent activities",
            
            # General conversational with time words
            "Good morning! How's everything today?",
            "I need help with something current",
            "What's the latest on my productivity?",
            "Recent changes in my routine"
        ]
        
        print("🧪 Testing PERSONAL queries (should NOT trigger web search):")
        false_positives = 0
        for query in personal_queries_with_ambiguous_keywords:
            should_search = smart_agent._requires_web_search(query)
            status = "❌ FALSE POSITIVE" if should_search else "✅ CORRECTLY IGNORED"
            print(f"   {status}: \"{query}\"")
            if should_search:
                false_positives += 1
        
        accuracy_personal = ((len(personal_queries_with_ambiguous_keywords) - false_positives) / 
                           len(personal_queries_with_ambiguous_keywords)) * 100
        print(f"\n📊 Personal Query Accuracy: {accuracy_personal:.1f}% ({false_positives} false positives)")
        
        # These should trigger web search (clear real-time info needs)
        clear_web_search_queries = [
            # Clear weather queries
            "What's the weather today in Mumbai?",
            "Today's weather forecast",
            "Temperature today in Delhi",
            "Is it raining today?",
            
            # Clear news queries
            "Latest news about AI",
            "What happened in today's election?",
            "Recent developments in technology",
            "Current events in politics",
            
            # Clear sports queries
            "Latest cricket score",
            "Who won today's match?",
            "Current football results",
            "Recent match updates",
            
            # Clear financial queries
            "Current stock price of Apple",
            "Latest market trends",
            "Today's cryptocurrency prices",
            "Recent market updates"
        ]
        
        print("\n🧪 Testing CLEAR WEB SEARCH queries (should trigger web search):")
        missed_detections = 0
        for query in clear_web_search_queries:
            should_search = smart_agent._requires_web_search(query)
            status = "✅ DETECTED" if should_search else "❌ MISSED"
            print(f"   {status}: \"{query}\"")
            if not should_search:
                missed_detections += 1
        
        accuracy_web = ((len(clear_web_search_queries) - missed_detections) / 
                       len(clear_web_search_queries)) * 100
        print(f"\n📊 Web Search Accuracy: {accuracy_web:.1f}% ({missed_detections} missed)")
        
        return false_positives == 0 and missed_detections <= 2  # Production standard: 0 false positives, max 2 misses
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases and tricky scenarios"""
    print("\n🎯 TESTING EDGE CASES")
    print("=" * 60)
    
    try:
        from core.smart_agent import SmartAgent
        smart_agent = SmartAgent.__new__(SmartAgent)
        
        # Edge cases that are tricky to classify
        edge_cases = {
            # Should NOT trigger web search
            "Personal/App queries": [
                "What's trending in my habits today?",  # Personal trending
                "Current status of my goals",           # Personal current
                "Latest update on my progress",         # Personal latest  
                "Recent changes I made",                # Personal recent
                "How's my productivity today?",         # Personal today
                "What's new with my vision board?",     # Personal new
                "Today I want to focus on fitness",     # Personal statement
                "Currently I'm working on meditation",  # Personal current state
            ],
            
            # Should trigger web search
            "Real-time information": [
                "What's trending today on social media?",  # Global trending
                "Current situation in Ukraine",            # Global current
                "Latest update on the pandemic",           # Global latest
                "Recent changes in government policy",     # Global recent
                "How's the economy doing today?",          # Global today
                "What's new in the tech industry?",        # Global new
                "Today's major headlines",                 # Global today
                "Currently happening natural disasters",   # Global current events
            ]
        }
        
        total_correct = 0
        total_queries = 0
        
        for category, queries in edge_cases.items():
            print(f"\n📂 {category}:")
            should_trigger = "Real-time information" in category
            category_correct = 0
            
            for query in queries:
                detected = smart_agent._requires_web_search(query)
                total_queries += 1
                
                if should_trigger:
                    status = "✅ DETECTED" if detected else "❌ MISSED"
                    if detected:
                        category_correct += 1
                        total_correct += 1
                else:
                    status = "✅ IGNORED" if not detected else "❌ FALSE POSITIVE"
                    if not detected:
                        category_correct += 1
                        total_correct += 1
                
                print(f"   {status}: \"{query}\"")
            
            accuracy = (category_correct / len(queries)) * 100
            print(f"   📊 Category Accuracy: {accuracy:.1f}%")
        
        overall_accuracy = (total_correct / total_queries) * 100
        print(f"\n🎯 Overall Edge Case Accuracy: {overall_accuracy:.1f}%")
        
        return overall_accuracy > 85  # Require 85%+ accuracy on edge cases
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        return False

def test_production_scenarios():
    """Test real production scenarios users might encounter"""
    print("\n🏭 TESTING PRODUCTION SCENARIOS")
    print("=" * 60)
    
    try:
        from core.smart_agent import SmartAgent
        smart_agent = SmartAgent.__new__(SmartAgent)
        
        # Real user scenarios from production logs (hypothetical but realistic)
        production_scenarios = [
            # Conversational greetings (should NOT search)
            ("Hey, how's your day going today?", False, "Greeting"),
            ("Good morning! What's new?", False, "Greeting"),
            ("Thanks for helping me yesterday", False, "Gratitude"), 
            
            # Personal productivity (should NOT search)
            ("I want to track my habits better today", False, "Personal productivity"),
            ("Show me my current goal progress", False, "Personal data"),
            ("What should I focus on this week?", False, "Personal planning"),
            
            # Clear information requests (should search)
            ("What's the weather like today in Tokyo?", True, "Weather query"),
            ("Latest cricket match scores", True, "Sports query"),
            ("Current stock market trends", True, "Financial query"),
            ("Recent news about artificial intelligence", True, "News query"),
            
            # Ambiguous but contextually clear (mixed)
            ("How's the market doing today?", True, "Financial - contextually clear"),
            ("What's happening in the world right now?", True, "News - contextually clear"),
            ("How are things going with the election?", True, "Current events"),
            ("What's the latest on COVID restrictions?", True, "Current policy/health"),
            
            # Tricky personal vs global
            ("How's my mood today?", False, "Personal state"),
            ("How's the economy today?", True, "Global state"),
            ("What's my current status?", False, "Personal status"),
            ("What's the current temperature?", True, "Environmental status"),
        ]
        
        print("🧪 Testing production scenarios:")
        correct_classifications = 0
        
        for query, expected_search, scenario_type in production_scenarios:
            actual_search = smart_agent._requires_web_search(query)
            is_correct = actual_search == expected_search
            
            if is_correct:
                correct_classifications += 1
                status = "✅ CORRECT"
            else:
                status = "❌ WRONG"
            
            expected_text = "SEARCH" if expected_search else "NO SEARCH"
            actual_text = "SEARCH" if actual_search else "NO SEARCH"
            
            print(f"   {status}: \"{query}\"")
            print(f"        Expected: {expected_text} | Actual: {actual_text} | Type: {scenario_type}")
        
        accuracy = (correct_classifications / len(production_scenarios)) * 100
        print(f"\n📊 Production Scenario Accuracy: {accuracy:.1f}% ({correct_classifications}/{len(production_scenarios)})")
        
        return accuracy > 90  # Production requires 90%+ accuracy
        
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PRODUCTION-READY WEB SEARCH DETECTION TEST")
    print("="*70)
    print("Testing advanced contextual analysis and ambiguous keyword handling...")
    
    # Run comprehensive tests
    ambiguous_test = test_ambiguous_keyword_handling()
    edge_case_test = test_edge_cases()
    production_test = test_production_scenarios()
    
    print("\n" + "="*70)
    print("🏁 PRODUCTION READINESS RESULTS")
    print("="*70)
    
    results = {
        "Ambiguous Keyword Handling": ambiguous_test,
        "Edge Case Detection": edge_case_test,
        "Production Scenarios": production_test
    }
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    if all(results.values()):
        print("\n🎉 PRODUCTION READY!")
        print("✅ Advanced contextual analysis working")
        print("✅ Ambiguous keywords handled correctly")
        print("✅ False positive rate minimized")
        print("✅ Edge cases properly classified")
        print("✅ Production scenarios validated")
        print("\n🛡️ PRODUCTION SAFETY FEATURES:")
        print("   ✅ Multi-phase detection with regex patterns")
        print("   ✅ Personal vs global context differentiation")
        print("   ✅ Explicit exclusion of personal/conversational queries")
        print("   ✅ Entity-based detection with contextual validation")
        print("   ✅ Question pattern analysis")
        print("   ✅ Safety checks to prevent false positives")
        print("\n✨ EXAMPLES OF IMPROVED DETECTION:")
        print("   ❌ 'How are you today?' → No web search (personal)")
        print("   ✅ 'Weather today in Mumbai?' → Web search (global info)")
        print("   ❌ 'My latest progress?' → No web search (personal)")  
        print("   ✅ 'Latest news about AI?' → Web search (current info)")
    else:
        print("\n⚠️ NOT READY FOR PRODUCTION")
        print("🔧 Issues detected that need fixing:")
        
        if not ambiguous_test:
            print("   - Ambiguous keyword handling needs improvement")
        if not edge_case_test:
            print("   - Edge case detection needs refinement")
        if not production_test:
            print("   - Production scenarios failing - review logic")
            
        print("\n🛠️ Recommended actions:")
        print("   1. Review false positive cases")
        print("   2. Enhance contextual patterns")
        print("   3. Add more exclusion rules")
        print("   4. Test with more user scenarios")
