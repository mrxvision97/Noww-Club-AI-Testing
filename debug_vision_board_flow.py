#!/usr/bin/env python3
"""
Debug script to test vision board generation flow
"""
import sys
sys.path.append('.')

from core.database import DatabaseManager
from core.memory import MemoryManager  
from core.vision_board_intake import VisionBoardIntakeManager
from core.vision_board_generator import VisionBoardGenerator

def debug_vision_board_flow():
    """Debug the vision board generation flow"""
    print("🔧 VISION BOARD FLOW DEBUG")
    print("=" * 50)
    
    # Initialize components
    db_manager = DatabaseManager()
    memory_manager = MemoryManager(db_manager)
    intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
    generator = VisionBoardGenerator(db_manager, memory_manager)
    
    test_user = "test_user_full_flow"  # User with completed intake
    
    print(f"📊 Testing with user: {test_user}")
    
    # Check intake status
    intake_status = intake_manager.get_intake_status(test_user)
    print(f"✅ Intake Status: {intake_status}")
    
    # Check episodic memories
    try:
        episodic_memories = memory_manager.get_vision_board_intake_memories(test_user)
        print(f"🧠 Episodic memories found: {len(episodic_memories) if episodic_memories else 0}")
        
        if episodic_memories:
            print("\nFirst memory sample:")
            first_memory = episodic_memories[0]
            print(f"   Theme: {first_memory.get('question_theme', 'N/A')}")
            print(f"   Response: {first_memory.get('raw_user_response', 'N/A')[:100]}...")
            analysis = first_memory.get('vision_analysis', {})
            print(f"   Colors: {analysis.get('color_palette', [])}")
            print(f"   Emotions: {analysis.get('core_emotions', [])}")
    except Exception as e:
        print(f"❌ Error getting episodic memories: {e}")
    
    # Check database intake
    try:
        db_intake = db_manager.get_vision_board_intake(test_user)
        print(f"📝 Database intake: {'Found' if db_intake else 'Not found'}")
        if db_intake:
            print(f"   Status: {db_intake.get('status', 'N/A')}")
            print(f"   Answers: {len(db_intake.get('answers', {}))}")
    except Exception as e:
        print(f"❌ Error getting database intake: {e}")
    
    # Test persona creation
    if intake_status.get("status") == "completed":
        print("\n🎭 Testing persona creation...")
        try:
            intake_answers = intake_manager.get_completed_answers(test_user)
            persona = generator.extract_persona_from_intake(test_user, intake_answers)
            print(f"✅ Persona created:")
            print(f"   Identity: {persona.get('core_identity', 'N/A')[:100]}...")
            print(f"   Colors: {persona.get('color_palette', [])}")
            print(f"   Symbols: {persona.get('visual_symbols', [])}")
            print(f"   From episodic: {persona.get('created_from_episodic_memory', False)}")
        except Exception as e:
            print(f"❌ Error creating persona: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Debug complete")

if __name__ == "__main__":
    debug_vision_board_flow()
