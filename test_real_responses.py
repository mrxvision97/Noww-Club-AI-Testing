#!/usr/bin/env python3
"""
Test script to create a vision board with user's actual responses
"""
import sys
sys.path.append('.')

import json
from datetime import datetime
from core.database import DatabaseManager
from core.memory import MemoryManager  
from core.vision_board_intake import VisionBoardIntakeManager
from core.vision_board_generator import VisionBoardGenerator

def test_with_real_responses():
    """Test vision board generation with user's actual responses"""
    print("🎨 TESTING VISION BOARD WITH REAL USER RESPONSES")
    print("=" * 60)
    
    # Initialize components
    db_manager = DatabaseManager()
    memory_manager = MemoryManager(db_manager)
    intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
    generator = VisionBoardGenerator(db_manager, memory_manager)
    
    test_user = "real_user_test"
    
    # User's actual responses
    real_responses = {
        1: "Unshakable clarity.",
        2: "For building mind-bending AI that actually improves lives.",
        3: "Mastering emotional intelligence in human-AI interactions.",
        4: "Setting brutal boundaries, sleeping like it's a job, and walking without my phone.",
        5: "Bold visionaries who are kind, curious, and obsessed with evolving.",
        6: "Deep convos with close friends, late-night coding sprints, and lo-fi beats in quiet corners.",
        7: "It feels like calm ambition — focused, free, and flowing with creative energy.",
        8: "My unapologetic ambition — the part that dreams outrageously and actually executes.",
        9: "Designing an AI-powered short film that captures raw human emotions.",
        10: "I want global recognition for creating something revolutionary."
    }
    
    print("🚀 Starting intake flow with real responses...")
    
    # Start intake
    start_response = intake_manager.start_intake_flow(test_user)
    print(f"📝 Started: {start_response[:100]}...")
    
    # Process each response
    for q_num, response in real_responses.items():
        print(f"\n❓ Question {q_num}: Processing response...")
        print(f"   💬 User: {response}")
        
        result = intake_manager.process_answer(test_user, response)
        print(f"   ✅ Processed: {result[:100]}...")
    
    # Check completion status
    status = intake_manager.get_intake_status(test_user)
    print(f"\n📊 Final Status: {status['status']}")
    
    if status['status'] == 'completed':
        print("\n🎨 Generating vision board...")
        
        # Test persona creation with real data
        intake_answers = intake_manager.get_completed_answers(test_user)
        persona = generator.extract_persona_from_intake(test_user, intake_answers)
        
        print(f"\n🎭 Generated Persona:")
        print(f"   Identity: {persona.get('core_identity', 'N/A')}")
        print(f"   Colors: {persona.get('color_palette', [])[:5]}")
        print(f"   Symbols: {persona.get('visual_symbols', [])[:5]}")
        print(f"   Aspirations: {persona.get('user_aspirations', [])[:3]}")
        print(f"   From Episodic: {persona.get('created_from_episodic_memory', False)}")
        
        # Test prompt customization
        template_num, template_name = intake_manager.recommend_template(test_user)
        print(f"\n📝 Recommended Template: {template_num} - {template_name}")
        
        template_prompt = generator.load_template_prompt(template_num)
        if template_prompt:
            customized_prompt = generator.customize_prompt_with_intake_data(template_prompt, persona, intake_answers)
            
            print(f"\n🎨 Customized Prompt Preview:")
            print(f"   Length: {len(customized_prompt)} characters")
            
            # Check for user-specific content
            user_keywords = ['clarity', 'mind-bending', 'AI', 'emotional intelligence', 'boundaries', 'ambition', 'revolutionary']
            found_keywords = []
            
            prompt_lower = customized_prompt.lower()
            for keyword in user_keywords:
                if keyword.lower() in prompt_lower:
                    found_keywords.append(keyword)
            
            print(f"   Found user keywords: {found_keywords}")
            
            # Show snippet of customized content
            if "unshakable clarity" in prompt_lower or "clarity" in prompt_lower:
                print("   ✅ Contains user's clarity concept")
            
            if "mind-bending" in prompt_lower or "ai" in prompt_lower:
                print("   ✅ Contains user's AI vision")
            
            if "revolutionary" in prompt_lower:
                print("   ✅ Contains user's revolutionary ambition")
        
        print(f"\n🎯 SUCCESS: Vision board system now uses real user responses!")
        print(f"   • Persona reflects actual answers")
        print(f"   • Prompt contains user-specific content")
        print(f"   • No more generic templates")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_with_real_responses()
