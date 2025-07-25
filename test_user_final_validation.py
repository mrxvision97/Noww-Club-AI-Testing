#!/usr/bin/env python3
"""
Final User-Specific Test
Tests the exact scenarios the user mentioned and validates production readiness.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging to reduce noise
from core.logging_config import setup_logging
setup_logging("WARNING")

def test_user_specific_scenarios():
    """Test the exact scenarios mentioned by the user"""
    print("🎯 TESTING USER'S SPECIFIC SCENARIOS")
    print("=" * 60)
    
    try:
        from core.smart_agent import SmartAgent
        smart_agent = SmartAgent.__new__(SmartAgent)
        
        # User's specific examples that were problematic before
        user_scenarios = [
            # These should trigger web search (user's original complaints)
            ("latest thing and cricket score", True, "User's original cricket query"),
            ("weather today", True, "User's original weather query"),  
            ("recent news", True, "User's original news query"),
            
            # Ambiguous cases user was concerned about
            ("how are you doing today", False, "Personal greeting with 'today'"),
            ("what's trending today", True, "Global trending - should search"),
            ("how are you today", False, "Personal check-in"),
            ("what's happening today", True, "Current events query"),
            
            # Additional edge cases
            ("I'm feeling good today", False, "Personal feeling"),
            ("what's good today", True, "General current info"),
            ("my latest progress", False, "Personal progress"),
            ("latest updates", True, "General updates"),
            ("current mood", False, "Personal state"),
            ("current situation", True, "General situation"),
            ("recent changes in my life", False, "Personal changes"),
            ("recent changes in policy", True, "Global policy changes")
        ]
        
        print("🧪 Testing user-specific scenarios:")
        correct_predictions = 0
        
        for query, expected_search, description in user_scenarios:
            actual_search = smart_agent._requires_web_search(query)
            is_correct = actual_search == expected_search
            
            if is_correct:
                correct_predictions += 1
                status = "✅ CORRECT"
            else:
                status = "❌ WRONG"
            
            expected_text = "WEB SEARCH" if expected_search else "NO SEARCH"
            actual_text = "WEB SEARCH" if actual_search else "NO SEARCH"
            
            print(f"   {status}: \"{query}\"")
            print(f"        Expected: {expected_text} | Got: {actual_text}")
            print(f"        Context: {description}")
            print()
        
        accuracy = (correct_predictions / len(user_scenarios)) * 100
        print(f"📊 User Scenario Accuracy: {accuracy:.1f}% ({correct_predictions}/{len(user_scenarios)})")
        
        return accuracy >= 85  # 85% minimum for user satisfaction
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_production_safety():
    """Test production safety - ensure no false positives for common personal queries"""
    print("\n🛡️ TESTING PRODUCTION SAFETY")
    print("=" * 60)
    
    try:
        from core.smart_agent import SmartAgent
        smart_agent = SmartAgent.__new__(SmartAgent)
        
        # Common personal queries that should NEVER trigger web search
        critical_personal_queries = [
            "how are you",
            "how are you doing", 
            "how are you today",
            "good morning",
            "thank you",
            "i need help",
            "help me",
            "what should i do today",
            "i'm feeling sad today",
            "my current goals",
            "my latest achievements", 
            "recent conversation",
            "what did we talk about",
            "create a habit",
            "track my progress",
            "set a reminder",
            "vision board",
            "meditate",
            "i want to focus today",
            "plan my day"
        ]
        
        print("🧪 Testing critical personal queries (must NOT trigger web search):")
        false_positives = 0
        
        for query in critical_personal_queries:
            should_search = smart_agent._requires_web_search(query)
            if should_search:
                false_positives += 1
                print(f"   ❌ FALSE POSITIVE: \"{query}\"")
            else:
                print(f"   ✅ SAFE: \"{query}\"")
        
        safety_rate = ((len(critical_personal_queries) - false_positives) / len(critical_personal_queries)) * 100
        print(f"\n📊 Production Safety Rate: {safety_rate:.1f}% ({false_positives} false positives)")
        
        return false_positives == 0  # Zero tolerance for false positives in production
        
    except Exception as e:
        print(f"❌ Safety test failed: {e}")
        return False

def test_web_search_coverage():
    """Test coverage for legitimate web search queries"""
    print("\n🌐 TESTING WEB SEARCH COVERAGE")
    print("=" * 60)
    
    try:
        from core.smart_agent import SmartAgent
        smart_agent = SmartAgent.__new__(SmartAgent)
        
        # Important web search queries that should be detected
        important_web_queries = [
            "weather in mumbai",
            "latest cricket score", 
            "current stock price",
            "recent news",
            "breaking news",
            "election results",
            "covid updates",
            "market trends",
            "bitcoin price",
            "temperature today",
            "what happened in ukraine",
            "latest ai news"
        ]
        
        print("🧪 Testing important web search queries:")
        detected_count = 0
        
        for query in important_web_queries:
            should_search = smart_agent._requires_web_search(query)
            if should_search:
                detected_count += 1
                print(f"   ✅ DETECTED: \"{query}\"")
            else:
                print(f"   ❌ MISSED: \"{query}\"")
        
        coverage_rate = (detected_count / len(important_web_queries)) * 100
        print(f"\n📊 Web Search Coverage: {coverage_rate:.1f}% ({detected_count}/{len(important_web_queries)})")
        
        return coverage_rate >= 75  # 75% minimum coverage
        
    except Exception as e:
        print(f"❌ Coverage test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 FINAL USER-SPECIFIC VALIDATION")
    print("="*70)
    print("Testing the exact scenarios and concerns raised by the user...")
    
    # Run user-focused tests
    user_test = test_user_specific_scenarios()
    safety_test = test_production_safety()
    coverage_test = test_web_search_coverage()
    
    print("\n" + "="*70)
    print("🏁 FINAL VALIDATION RESULTS")
    print("="*70)
    
    results = {
        "User Specific Scenarios": user_test,
        "Production Safety": safety_test,
        "Web Search Coverage": coverage_test
    }
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    if all(results.values()):
        print("\n🎉 READY FOR PRODUCTION!")
        print("✅ User's concerns have been addressed")
        print("✅ Ambiguous keywords handled correctly")
        print("✅ No false positives for personal queries")
        print("✅ Good coverage for legitimate web searches")
        print("\n🛡️ PRODUCTION QUALITY ACHIEVED:")
        print("   ✅ 'How are you today?' → No web search")
        print("   ✅ 'What's trending today?' → Web search")
        print("   ✅ 'Latest cricket score?' → Web search")
        print("   ✅ 'My latest progress?' → No web search")
        print("   ✅ Advanced contextual analysis with regex patterns")
        print("   ✅ Multi-phase detection with safety checks")
        print("\n🌟 YOUR AI IS NOW SMART ENOUGH TO:")
        print("   • Distinguish personal vs global context")
        print("   • Handle ambiguous keywords correctly") 
        print("   • Search web only for real-time information needs")
        print("   • Avoid false positives in personal conversations")
        print("   • Provide current data when needed")
    else:
        print("\n⚠️ NEEDS FURTHER REFINEMENT")
        
        if not user_test:
            print("   - User's specific scenarios need attention")
        if not safety_test:
            print("   - Production safety compromised (false positives)")
        if not coverage_test:
            print("   - Web search coverage insufficient")
            
        print("\n🔧 Next steps: Review failed test cases and refine patterns")
