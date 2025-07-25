#!/usr/bin/env python3
"""
Test script for the enhanced vision board generation approach
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_vision_board():
    """Test the enhanced vision board generation"""
    try:
        print("🚀 Testing Enhanced Vision Board Generation...")
        
        # Import components
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.vision_board_generator import VisionBoardGenerator
        from core.vision_board_intake import VisionBoardIntakeManager
        
        print("✅ All imports successful")
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        vision_generator = VisionBoardGenerator(db_manager, memory_manager)
        
        print("✅ Components initialized")
        
        # Test user ID
        test_user_id = "test_enhanced_user"
        
        # Sample persona (like the example you provided)
        sample_persona = {
            "user_id": test_user_id,
            "name": "Test User",
            "age": "25-30",
            "core_identity": "Bold visionary focused on building mind-bending AI that improves lives",
            "dominant_emotions": ["unshakable clarity", "focused ambition", "creative innovation"],
            "life_aspirations": [
                "Building mind-bending AI that actually improves lives",
                "Global recognition for creating something revolutionary", 
                "Mastering emotional intelligence in human-AI interactions",
                "Designing an AI-powered short film that captures raw human emotions"
            ],
            "visual_symbols": ["eye of digital storm", "calm ambition", "creative energy flow", "late-night coding"],
            "color_palette": ["calm ambition tones", "focused energy", "creative flow colors"],
            "lifestyle_desires": ["deep convos with close friends", "late-night coding sprints", "lo-fi beats in quiet corners"],
            "core_values": ["brutal boundaries", "unapologetic ambition", "bold visionary thinking"],
            "energy_vibe": "calm ambition",
            "visual_style": "focused and flowing"
        }
        
        # Sample intake answers (like your example)
        sample_intake_answers = {
            "1": {
                "answer": "Unshakable clarity.",
                "theme": "emotional_anchor",
                "timestamp": datetime.now().isoformat()
            },
            "2": {
                "answer": "For building mind-bending AI that actually improves lives.",
                "theme": "identity_legacy", 
                "timestamp": datetime.now().isoformat()
            },
            "3": {
                "answer": "Mastering emotional intelligence in human-AI interactions.",
                "theme": "growth_craft",
                "timestamp": datetime.now().isoformat()
            },
            "4": {
                "answer": "Setting brutal boundaries, sleeping like it's a job, and walking without my phone.",
                "theme": "self_care_wellness",
                "timestamp": datetime.now().isoformat()
            },
            "5": {
                "answer": "Bold visionaries who are kind, curious, and obsessed with evolving.",
                "theme": "relationships_community",
                "timestamp": datetime.now().isoformat()
            },
            "6": {
                "answer": "Deep convos with close friends, late-night coding sprints, and lo-fi beats in quiet corners.",
                "theme": "authentic_presence",
                "timestamp": datetime.now().isoformat()
            },
            "7": {
                "answer": "It feels like calm ambition — focused, free, and flowing with creative energy.",
                "theme": "space_environment",
                "timestamp": datetime.now().isoformat()
            },
            "8": {
                "answer": "My unapologetic ambition — the part that dreams outrageously and actually executes.",
                "theme": "unleashed_expression",
                "timestamp": datetime.now().isoformat()
            },
            "9": {
                "answer": "Designing an AI-powered short film that captures raw human emotions.",
                "theme": "secret_desire",
                "timestamp": datetime.now().isoformat()
            },
            "10": {
                "answer": "I want global recognition for creating something revolutionary.",
                "theme": "brave_wish",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        print("📝 Testing enhanced LLM prompt generation...")
        
        # Test the enhanced LLM prompt generation
        enhanced_prompt = vision_generator.create_enhanced_llm_prompt(sample_persona, sample_intake_answers)
        
        if enhanced_prompt:
            print("✅ Enhanced LLM prompt generated successfully!")
            print(f"📏 Prompt length: {len(enhanced_prompt)} characters")
            print("\n🎨 SAMPLE OF GENERATED PROMPT:")
            print("=" * 60)
            print(enhanced_prompt[:500] + "...")
            print("=" * 60)
            
            # Test the complete integration
            print("\n🔄 Testing complete prompt customization...")
            template_prompt = "Sample template prompt"  # This will be ignored in favor of enhanced approach
            
            final_prompt = vision_generator.customize_prompt_with_intake_data(
                template_prompt, sample_persona, sample_intake_answers
            )
            
            if final_prompt:
                print("✅ Complete integration test successful!")
                print(f"📏 Final prompt length: {len(final_prompt)} characters")
                print("🎯 Enhanced approach is working correctly!")
                
                return True
            else:
                print("❌ Complete integration test failed")
                return False
        else:
            print("❌ Enhanced LLM prompt generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_vision_board()
    if success:
        print("\n🎉 ENHANCED VISION BOARD GENERATION TEST PASSED!")
        print("🚀 The new approach is ready to create sophisticated, personalized vision boards!")
    else:
        print("\n💥 Test failed - please check the implementation")
    
    exit(0 if success else 1)
