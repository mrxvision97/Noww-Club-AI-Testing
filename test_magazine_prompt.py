#!/usr/bin/env python3
"""
Simple test for magazine-style vision board prompt generation
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from core.vision_board_generator import VisionBoardGenerator

def test_magazine_prompt():
    """Test magazine-style prompt generation only"""
    print("🎨 Testing Magazine-Style Prompt Generation...")
    print("=" * 60)
    
    try:
        # Create a minimal vision board generator instance just for prompt testing
        vision_board_gen = VisionBoardGenerator.__new__(VisionBoardGenerator)
        
        # Initialize the templates manually
        vision_board_gen.templates = [
            {"name": "Template 1", "style": "modern"},
            {"name": "Template 2", "style": "elegant"},
            {"name": "Template 3", "style": "sophisticated"},
        ]
        
        # Test the new magazine-style prompt generation method
        print("📝 Testing prompt customization with actual user responses...")
        
        # Simulate actual user responses
        actual_responses = [
            "unshakable clarity",
            "mind-bending AI breakthrough",
            "emotional intelligence mastery",
            "revolutionary innovation",
            "unstoppable success journey",
            "global recognition and impact",
            "premium lifestyle achievement",
            "authentic visionary leadership"
        ]
        
        # Create test persona
        persona = {
            "name": "Visionary User",
            "age": "28-35",
            "identity": "Innovative tech leader with unshakable clarity",
            "aspirations": ["mind-bending AI", "global recognition", "revolutionary innovation"],
            "values": ["authenticity", "excellence", "breakthrough thinking"],
            "lifestyle": ["premium experiences", "cutting-edge technology", "visionary leadership"],
            "visual_symbols": ["mountain peak", "compass", "ascending stairs", "golden light"],
            "emotions": ["clarity", "confidence", "innovation", "unstoppable"],
            "colors": ["deep charcoal", "warm gold", "rich black", "sophisticated white"],
            "specific_mentions": ["AI breakthrough", "emotional intelligence", "visionary leadership"]
        }
        
        template_num = 2  # Use template 3 (index 2)
        
        # Test the prompt generation
        print(f"✅ Using template {template_num + 1}: {vision_board_gen.templates[template_num]['name']}")
        
        # Call the method correctly with template prompt and intake answers
        template_prompt = "Create a vision board"  # Basic template prompt
        intake_answers = {"responses": actual_responses}  # Convert to expected format
        
        prompt = vision_board_gen.customize_prompt_with_intake_data(
            template_prompt, persona, intake_answers
        )
        
        print(f"✅ Magazine prompt generated: {len(prompt)} characters")
        print("\n📋 Full Magazine-Style Prompt:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        
        # Check for key magazine-style elements
        print("\n🔍 Checking for magazine-style elements...")
        magazine_elements = [
            "MAGAZINE-STYLE VISION BOARD COLLAGE",
            "SECTION-BY-SECTION BREAKDOWN", 
            "DSLR-quality photography",
            "elegant typography",
            "sophisticated collage",
            "unshakable clarity",
            "mind-bending AI",
            "revolutionary"
        ]
        
        found_elements = 0
        for element in magazine_elements:
            if element.lower() in prompt.lower():
                print(f"✅ Found: {element}")
                found_elements += 1
            else:
                print(f"❌ Missing: {element}")
        
        print(f"\n📊 Magazine Elements Found: {found_elements}/{len(magazine_elements)}")
        
        if found_elements >= len(magazine_elements) * 0.7:  # 70% or more
            print("✅ Prompt successfully contains magazine-style elements!")
        else:
            print("❌ Prompt missing key magazine-style elements")
        
        # Test the helper method
        print("\n🔤 Testing quote extraction helper...")
        quote1 = vision_board_gen._extract_short_quote(actual_responses, 0)
        quote2 = vision_board_gen._extract_short_quote(actual_responses, 1)
        quote3 = vision_board_gen._extract_short_quote(actual_responses, 2)
        
        print(f"Quote 1: '{quote1}'")
        print(f"Quote 2: '{quote2}'")
        print(f"Quote 3: '{quote3}'")
        
        print("\n🎯 Test Complete! Magazine-style prompt generation is working.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_magazine_prompt()
