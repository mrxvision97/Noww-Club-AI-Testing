#!/usr/bin/env python3
"""
Test Episodic Memory Vision Board System
Tests the new authentic personalization using episodic memory
"""

import os
import sys
import json
from datetime import datetime

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import DatabaseManager
from core.memory import MemoryManager
from core.vision_board_intake import VisionBoardIntakeManager
from core.vision_board_generator import VisionBoardGenerator

def test_episodic_memory_vision_board():
    """Test the complete episodic memory-based vision board system"""
    print("🧪 TESTING EPISODIC MEMORY VISION BOARD SYSTEM")
    print("=" * 60)
    
    try:
        # Initialize components
        print("🔧 Initializing system components...")
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
        vision_generator = VisionBoardGenerator(db_manager, memory_manager)
        
        test_user_id = "test_episodic_user"
        
        # Clear any existing data
        print(f"🧹 Clearing existing data for {test_user_id}...")
        try:
            memory_manager.clear_user_memory(test_user_id)
            intake_manager._clear_intake_data(test_user_id)
        except:
            pass
        
        print("✅ System components initialized")
        
        # Test 1: Store sample intake responses in episodic memory
        print("\n📝 TEST 1: Storing sample intake responses in episodic memory")
        print("-" * 50)
        
        sample_responses = [
            {
                "question_num": 1,
                "question_data": {
                    "theme": "life_vision",
                    "question": "What does your ideal life look like?",
                    "context": "Vision and aspirations"
                },
                "raw_answer": "I want a peaceful life surrounded by nature, with a cozy home where I can read books and grow plants. I dream of writing novels and traveling to quiet mountains.",
                "analyzed_data": {
                    "core_emotions": ["peaceful", "content", "inspired", "creative"],
                    "visual_metaphors": ["mountains", "cozy home", "books", "plants", "nature"],
                    "color_palette": ["forest green", "earth brown", "soft cream", "mountain blue"],
                    "lifestyle_elements": ["quiet spaces", "natural environment", "reading nooks", "garden"],
                    "values_revealed": ["peace", "creativity", "nature", "solitude"],
                    "aspirations": ["write novels", "travel to mountains", "live in nature", "creative life"],
                    "personality_traits": ["introspective", "creative", "nature-loving", "peaceful"],
                    "essence_keywords": ["peace", "nature", "creativity", "books", "mountains"],
                    "specific_mentions": ["novels", "mountains", "plants", "cozy home"],
                    "visual_style_preference": "natural",
                    "energy_level": "calm",
                    "authenticity_score": "9",
                    "manifestation_focus": ["creative writing", "mountain home"],
                    "symbolic_elements": ["growing things", "quiet paths", "written words"]
                }
            },
            {
                "question_num": 2,
                "question_data": {
                    "theme": "personal_growth", 
                    "question": "What personal qualities do you want to develop?",
                    "context": "Self-improvement focus"
                },
                "raw_answer": "I want to become more confident in sharing my writing with others. I'd love to be patient like a wise tree and have the courage to speak my truth.",
                "analyzed_data": {
                    "core_emotions": ["hopeful", "determined", "vulnerable", "wise"],
                    "visual_metaphors": ["wise tree", "growing confidence", "speaking truth", "sharing light"],
                    "color_palette": ["golden yellow", "tree bark brown", "sunrise orange", "sage green"],
                    "lifestyle_elements": ["writing space", "sharing circles", "wisdom practices"],
                    "values_revealed": ["authenticity", "courage", "patience", "truth"],
                    "aspirations": ["confident sharing", "wise patience", "truthful expression"],
                    "personality_traits": ["thoughtful", "growth-oriented", "creative", "authentic"],
                    "essence_keywords": ["confidence", "wisdom", "truth", "patience", "sharing"],
                    "specific_mentions": ["writing", "wise tree", "speak truth"],
                    "visual_style_preference": "organic",
                    "energy_level": "medium",
                    "authenticity_score": "8",
                    "manifestation_focus": ["confident expression", "wise patience"],
                    "symbolic_elements": ["tree wisdom", "growing confidence", "truth light"]
                }
            }
        ]
        
        # Store each response in episodic memory
        for response in sample_responses:
            memory_manager.add_vision_board_intake_to_episodic_memory(
                test_user_id,
                response["question_num"],
                response["question_data"],
                response["raw_answer"],
                response["analyzed_data"]
            )
            print(f"✅ Stored Q{response['question_num']} in episodic memory")
        
        print(f"✅ Stored {len(sample_responses)} responses in episodic memory")
        
        # Test 2: Retrieve episodic memories
        print("\n📖 TEST 2: Retrieving episodic memories")
        print("-" * 50)
        
        retrieved_memories = memory_manager.get_vision_board_intake_memories(test_user_id)
        print(f"📊 Retrieved {len(retrieved_memories)} episodic memories")
        
        for memory in retrieved_memories:
            print(f"   • Q{memory.get('question_number')}: {memory.get('question_theme')} - {memory.get('raw_user_response')[:50]}...")
        
        if len(retrieved_memories) == len(sample_responses):
            print("✅ Episodic memory retrieval successful")
        else:
            print(f"❌ Expected {len(sample_responses)}, got {len(retrieved_memories)}")
            return False
        
        # Test 3: Create authentic persona from episodic memory
        print("\n👤 TEST 3: Creating authentic persona from episodic memory")
        print("-" * 50)
        
        # Create fake intake answers for fallback (should not be used)
        fake_intake_answers = {"1": {"answer": "fake", "theme": "fake"}}
        
        persona = vision_generator.extract_persona_from_intake(test_user_id, fake_intake_answers)
        
        print(f"📊 Persona created:")
        print(f"   • Core identity: {persona.get('core_identity', 'Unknown')}")
        print(f"   • Visual symbols: {persona.get('visual_symbols', [])[:3]}")
        print(f"   • Color palette: {persona.get('color_palette', [])[:3]}")
        print(f"   • Life aspirations: {persona.get('life_aspirations', [])[:3]}")
        print(f"   • Created from episodic memory: {persona.get('created_from_episodic_memory', False)}")
        
        if persona.get('created_from_episodic_memory'):
            print("✅ Authentic persona created from episodic memory")
            
            # Check for authentic content
            authentic_checks = {
                "nature_elements": any("nature" in str(item).lower() or "mountain" in str(item).lower() or "tree" in str(item).lower() 
                                    for item in persona.get('visual_symbols', [])),
                "creative_elements": any("writing" in str(item).lower() or "creative" in str(item).lower() or "novel" in str(item).lower()
                                       for item in persona.get('life_aspirations', [])),
                "peaceful_colors": any("green" in str(item).lower() or "brown" in str(item).lower() or "cream" in str(item).lower()
                                     for item in persona.get('color_palette', [])),
                "authentic_emotions": any("peaceful" in str(item).lower() or "wise" in str(item).lower()
                                        for item in persona.get('dominant_emotions', []))
            }
            
            passed_checks = sum(authentic_checks.values())
            print(f"📊 Authenticity checks: {passed_checks}/4 passed")
            
            for check, passed in authentic_checks.items():
                print(f"   • {check}: {'✅' if passed else '❌'}")
                
            if passed_checks >= 3:
                print("✅ Persona contains authentic user-specific content")
            else:
                print("❌ Persona lacks authentic user-specific content")
                return False
        else:
            print("❌ Persona was not created from episodic memory")
            return False
        
        # Test 4: Create authentic vision board prompt
        print("\n🎨 TEST 4: Creating authentic vision board prompt")
        print("-" * 50)
        
        # Add user_id to persona
        persona['user_id'] = test_user_id
        
        template_prompt = "Basic template prompt for testing"
        authentic_prompt = vision_generator.customize_prompt_with_intake_data(
            template_prompt, persona, fake_intake_answers
        )
        
        print(f"📊 Authentic prompt created ({len(authentic_prompt)} characters)")
        
        # Check for authentic content in prompt
        prompt_checks = {
            "breaks_from_generic": "NO generic" in authentic_prompt and "NOT black/gold" in authentic_prompt,
            "user_specific_colors": any(color in authentic_prompt.lower() for color in ["green", "brown", "cream", "blue"]),
            "user_specific_symbols": any(symbol in authentic_prompt.lower() for symbol in ["mountain", "tree", "book", "plant"]),
            "user_aspirations": any(aspiration in authentic_prompt.lower() for aspiration in ["writing", "novel", "creative"]),
            "authentic_story": "USER'S AUTHENTIC STORY" in authentic_prompt
        }
        
        passed_prompt_checks = sum(prompt_checks.values())
        print(f"📊 Prompt authenticity checks: {passed_prompt_checks}/5 passed")
        
        for check, passed in prompt_checks.items():
            print(f"   • {check}: {'✅' if passed else '❌'}")
        
        if passed_prompt_checks >= 4:
            print("✅ Prompt contains authentic, personalized content")
        else:
            print("❌ Prompt lacks sufficient personalization")
            return False
        
        # Test 5: Verify no generic content
        print("\n🚫 TEST 5: Verifying removal of generic content")
        print("-" * 50)
        
        generic_elements = ["black and gold", "luxury car", "generic flower", "standard success", "template-driven"]
        generic_found = [element for element in generic_elements if element.lower() in authentic_prompt.lower()]
        
        if not generic_found:
            print("✅ No generic content found in authentic prompt")
        else:
            print(f"❌ Found generic content: {generic_found}")
            return False
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 EPISODIC MEMORY VISION BOARD TEST SUMMARY")
        print("=" * 60)
        
        print(f"✅ Episodic memory storage: PASSED")
        print(f"✅ Episodic memory retrieval: PASSED") 
        print(f"✅ Authentic persona creation: PASSED")
        print(f"✅ Authentic prompt generation: PASSED")
        print(f"✅ Generic content removal: PASSED")
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"📈 Vision board system now uses authentic episodic memory data")
        print(f"🎨 Generated vision boards will be completely personalized")
        print(f"🚫 No more generic black/gold templates")
        print(f"✨ Each vision board will be uniquely authentic to the user")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_episodic_memory_vision_board()
    if success:
        print(f"\n🎯 READY FOR PRODUCTION: Episodic memory vision board system is working!")
    else:
        print(f"\n⚠️ NEEDS FIXES: Check the errors above")
