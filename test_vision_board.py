#!/usr/bin/env python3
"""
Test script for vision board functionality
This script tests the vision board generation without requiring the full UI
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_vision_board_imports():
    """Test if all vision board related imports work"""
    print("🧪 Testing vision board imports...")
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.smart_agent import SmartAgent
        from core.vision_board_generator import VisionBoardGenerator
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_vision_board_initialization():
    """Test if vision board generator can be initialized"""
    print("\n🧪 Testing vision board initialization...")
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.vision_board_generator import VisionBoardGenerator
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        vision_generator = VisionBoardGenerator(db_manager, memory_manager)
        
        print("✅ Vision board generator initialized successfully")
        print(f"📋 Available templates: {len(vision_generator.templates)}")
        
        # Test template analysis (without user data)
        test_template = vision_generator.analyze_user_for_template("test_user")
        print(f"🎯 Default template selection: {test_template}")
        
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_vision_board_prompts():
    """Test if vision board prompts can be loaded"""
    print("\n🧪 Testing vision board prompt loading...")
    
    try:
        from core.vision_board_generator import VisionBoardGenerator
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        vision_generator = VisionBoardGenerator(db_manager, memory_manager)
        
        # Test loading each template prompt
        for template_num in range(1, 5):
            prompt = vision_generator.load_template_prompt(template_num)
            if prompt:
                print(f"✅ Template {template_num} prompt loaded ({len(prompt)} characters)")
            else:
                print(f"❌ Template {template_num} prompt failed to load")
        
        return True
    except Exception as e:
        print(f"❌ Prompt loading error: {e}")
        return False

def test_smart_agent_integration():
    """Test if smart agent properly integrates vision board generator"""
    print("\n🧪 Testing smart agent integration...")
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.smart_agent import SmartAgent
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        # Check if vision board generator is properly initialized
        if hasattr(smart_agent, 'vision_board_generator'):
            print("✅ Smart agent has vision board generator")
            
            # Test vision board intent detection
            test_messages = [
                "create a vision board",
                "I want to visualize my dreams",
                "show me my future goals",
                "hello how are you"  # Should not trigger
            ]
            
            for msg in test_messages:
                is_vision_request = smart_agent.check_for_vision_board_intent(msg)
                print(f"📝 '{msg}' -> Vision board intent: {is_vision_request}")
            
            return True
        else:
            print("❌ Smart agent missing vision board generator")
            return False
            
    except Exception as e:
        print(f"❌ Smart agent integration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Vision Board Functionality Tests")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Vision board generation will fail.")
    else:
        print("✅ OpenAI API key is configured")
    
    tests = [
        test_vision_board_imports,
        test_vision_board_initialization,
        test_vision_board_prompts,
        test_smart_agent_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Vision board functionality is ready!")
        print("\n💡 To use vision boards:")
        print("   1. Start the app with: streamlit run app.py")
        print("   2. Log in to the application")
        print("   3. Say something like: 'Create a vision board for me'")
        print("   4. Wait for the personalized vision board to be generated")
        print("   5. Download your vision board when ready!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
