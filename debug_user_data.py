#!/usr/bin/env python3
"""
Debug test to see what's happening with the user data extraction
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager
from core.memory import MemoryManager
from core.vision_board_generator import VisionBoardGenerator

def debug_user_data_flow():
    """Debug the flow of user data through the system"""
    print("🔍 Debugging User Data Flow")
    print("=" * 50)
    
    # Initialize components
    db_manager = DatabaseManager()
    memory_manager = MemoryManager()
    generator = VisionBoardGenerator(db_manager, memory_manager)
    
    # Test with a user who has completed intake
    test_user_id = "test_user_vision_board"  # From your previous tests
    
    print(f"👤 Testing with user: {test_user_id}")
    
    # Step 1: Check if intake is complete
    print("\n1️⃣ Checking intake completion...")
    try:
        is_complete = generator.intake_manager.is_intake_complete(test_user_id)
        print(f"   Intake complete: {is_complete}")
        
        if not is_complete:
            print("   ❌ User hasn't completed intake - creating test data...")
            # Create test intake data
            test_answers = {
                0: {
                    "answer": "I want to feel deeply connected to nature and find inner peace through daily meditation",
                    "analysis": {
                        "core_emotions": ["peaceful", "connected", "serene", "grounded"],
                        "visual_metaphors": ["flowing water", "mountain peaks", "zen gardens", "lotus flowers"],
                        "color_palette": ["soft greens", "earth tones", "gentle blues", "warm whites"],
                        "lifestyle_elements": ["meditation spaces", "natural environments", "peaceful gardens"],
                        "values_revealed": ["mindfulness", "inner peace", "nature connection"],
                        "aspirations": ["spiritual growth", "daily meditation practice", "natural living"],
                        "essence_keywords": ["nature", "peace", "meditation", "connection", "serenity"],
                        "energy_level": "medium",
                        "visual_style_preference": "natural"
                    }
                },
                1: {
                    "answer": "I envision myself as a confident entrepreneur running a sustainable wellness business",
                    "analysis": {
                        "core_emotions": ["confident", "empowered", "determined", "visionary"],
                        "visual_metaphors": ["rising sun", "strong foundations", "growing plants", "clear pathways"],
                        "color_palette": ["bold greens", "gold accents", "confident blues", "earth tones"],
                        "lifestyle_elements": ["modern offices", "wellness centers", "sustainable spaces"],
                        "values_revealed": ["sustainability", "entrepreneurship", "wellness", "confidence"],
                        "aspirations": ["business success", "sustainable impact", "wellness leadership"],
                        "essence_keywords": ["entrepreneur", "sustainable", "wellness", "business", "confident"],
                        "energy_level": "high", 
                        "visual_style_preference": "bold"
                    }
                }
            }
            
            # Store test answers in database
            for q_num, data in test_answers.items():
                try:
                    generator.intake_manager._store_answer(test_user_id, q_num, data["answer"], data["analysis"])
                except Exception as e:
                    print(f"   Error storing test answer {q_num}: {e}")
            
            print("   ✅ Test data created")
    
    except Exception as e:
        print(f"   ❌ Error checking intake: {e}")
        return
    
    # Step 2: Get intake answers
    print("\n2️⃣ Retrieving intake answers...")
    try:
        intake_answers = generator.intake_manager.get_completed_answers(test_user_id)
        print(f"   Found {len(intake_answers)} answers")
        
        # Show what we actually got
        for q_num, answer_data in intake_answers.items():
            print(f"   Q{q_num}: {answer_data.get('answer', 'No answer')[:50]}...")
            if 'analysis' in answer_data:
                analysis = answer_data['analysis']
                print(f"        Emotions: {analysis.get('core_emotions', [])[:3]}")
                print(f"        Colors: {analysis.get('color_palette', [])[:3]}")
            else:
                print(f"        ❌ No analysis data found")
        
    except Exception as e:
        print(f"   ❌ Error getting answers: {e}")
        return
    
    # Step 3: Test persona extraction
    print("\n3️⃣ Testing persona extraction...")
    try:
        # Test the extract_persona_from_intake method
        persona = generator.extract_persona_from_intake(test_user_id, intake_answers)
        print(f"   ✅ Persona created successfully")
        print(f"   Core Identity: {persona.get('core_identity', 'Not found')}")
        print(f"   Values: {persona.get('values', [])}")
        print(f"   Life Goals: {persona.get('life_goals', [])}")
        
    except Exception as e:
        print(f"   ❌ Error creating persona: {e}")
        import traceback
        traceback.print_exc()
        
        # Use a basic persona for testing
        persona = {
            "name": "Test User",
            "age": "25-35",
            "personality": "Authentic and growth-oriented person seeking balance",
            "core_identity": "Someone who values mindfulness and entrepreneurial spirit",
            "values": ["mindfulness", "sustainability", "authenticity", "growth"],
            "life_goals": ["spiritual growth", "business success", "wellness leadership"],
            "emotional_core": ["peaceful", "confident", "determined"],
            "visual_preferences": ["natural", "bold", "inspiring"],
            "lifestyle_desires": ["meditation spaces", "wellness centers", "sustainable environments"],
            "energy_vibe": "balanced and focused",
            "key_essence_words": ["nature", "peace", "entrepreneur", "wellness", "growth"]
        }
        print("   🔄 Using fallback persona for testing")
    
    # Step 4: Test prompt customization
    print("\n4️⃣ Testing prompt customization...")
    try:
        # Load a template
        template_prompt = generator.load_template_prompt(1)
        if not template_prompt:
            template_prompt = "Create a beautiful vision board for {USER_NAME} who values {USER_VALUES} and dreams of {USER_GOALS}."
        
        print(f"   Template loaded: {len(template_prompt)} characters")
        
        # Test customization
        customized_prompt = generator.customize_prompt_with_intake_data(template_prompt, persona, intake_answers)
        print(f"   ✅ Customization successful: {len(customized_prompt)} characters")
        
        # Check if user data appears in the prompt
        prompt_lower = customized_prompt.lower()
        checks = {
            "meditation": "meditation" in prompt_lower,
            "nature": "nature" in prompt_lower,
            "entrepreneur": "entrepreneur" in prompt_lower,
            "wellness": "wellness" in prompt_lower,
            "peaceful": "peaceful" in prompt_lower,
            "confident": "confident" in prompt_lower
        }
        
        found = sum(checks.values())
        total = len(checks)
        
        print(f"   📊 User elements in prompt: {found}/{total} ({found/total*100:.1f}%)")
        for key, found_flag in checks.items():
            status = "✅" if found_flag else "❌"
            print(f"      {status} {key}")
        
        # Show a sample of the customized prompt
        print(f"\n   📖 Prompt sample (first 300 chars):")
        print(f"      {customized_prompt[:300]}...")
        
    except Exception as e:
        print(f"   ❌ Error in customization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_user_data_flow()
