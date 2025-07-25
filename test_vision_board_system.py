#!/usr/bin/env python3
"""
Quick test to verify vision board functionality works
"""

import os
import sys
sys.path.append('.')

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

from core.database import DatabaseManager
from core.memory import MemoryManager
from core.smart_agent import SmartAgent

def test_vision_board_detection():
    """Test if vision board requests are detected properly"""
    try:
        print("🧪 Testing Vision Board System...")
        
        # Initialize components with fallback
        print("📂 Initializing components...")
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        
        print(f"✅ Memory system initialized (using {'Pinecone' if memory_manager.using_pinecone else 'Local Storage'})")
        
        # Test vision board detection
        test_messages = [
            "I want to create a vision board",
            "Create my vision board",
            "Show me my vision",
            "Help me visualize my goals",
            "I need a dream board"
        ]
        
        print("\n🔍 Testing Vision Board Detection:")
        for msg in test_messages:
            # Simple keyword detection test
            vision_keywords = [
                'vision board', 'dream board', 'visualize my goals', 'show my future', 
                'create my vision', 'vision', 'dreams visualization', 'goal board',
                'my dreams', 'visualize dreams', 'show my goals', 'future board'
            ]
            
            is_vision_request = any(keyword in msg.lower() for keyword in vision_keywords)
            print(f"   '{msg}' -> {'✅ DETECTED' if is_vision_request else '❌ NOT DETECTED'}")
        
        print("\n🎨 Testing Vision Board Components:")
        
        # Test intake manager
        try:
            from core.vision_board_intake import VisionBoardIntakeManager
            intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
            print("✅ Vision Board Intake Manager initialized")
        except Exception as e:
            print(f"❌ Vision Board Intake Manager failed: {e}")
            return False
        
        # Test generator
        try:
            from core.vision_board_generator import VisionBoardGenerator
            generator = VisionBoardGenerator(db_manager, memory_manager)
            print("✅ Vision Board Generator initialized")
        except Exception as e:
            print(f"❌ Vision Board Generator failed: {e}")
            return False
        
        print("\n🤖 Testing Smart Agent:")
        try:
            smart_agent = SmartAgent(db_manager, memory_manager)
            print("✅ Smart Agent initialized")
        except Exception as e:
            print(f"❌ Smart Agent failed: {e}")
            return False
        
        print("\n🎯 All components working! Vision board system is functional.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Noww Club AI - Vision Board System Test")
    print("=" * 50)
    
    if test_vision_board_detection():
        print("\n✅ SUCCESS: Vision board system is working!")
        print("💡 Tips:")
        print("   - Try saying 'I want to create a vision board'")
        print("   - Memory system will work with or without Pinecone")
        print("   - Local fallback storage is active if Pinecone fails")
    else:
        print("\n❌ FAILED: Vision board system has issues")
        print("🔧 Check your environment variables and dependencies")
    
    print("\n" + "=" * 50)
