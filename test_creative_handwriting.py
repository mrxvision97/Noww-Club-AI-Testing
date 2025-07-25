#!/usr/bin/env python3
"""
Test Creative Vision Board Features with Handwriting and Creative Layouts
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_creative_handwriting_features():
    """Test the new creative features including handwriting and layout flexibility"""
    print("✍️ TESTING CREATIVE VISION BOARD WITH HANDWRITING & LAYOUTS")
    print("=" * 70)
    print()
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.vision_board_generator import VisionBoardGenerator
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        vision_generator = VisionBoardGenerator(db_manager, memory_manager)
        
        # Test persona for creative artist
        creative_artist_persona = {
            "user_id": "creative_artist_user",
            "core_identity": "Creative entrepreneur building a lifestyle brand with authentic storytelling",
            "dominant_emotions": ["inspired creativity", "gentle confidence", "flowing energy"],
            "life_aspirations": [
                "Launching my own creative studio",
                "Writing a bestselling book about creativity",
                "Building a community of fellow artists",
                "Creating art that changes lives"
            ],
            "visual_symbols": ["flowing water", "blooming flowers", "open books", "artistic brushes"],
            "color_palette": ["soft pastels", "warm earth tones", "golden sunlight", "sage greens"],
            "lifestyle_desires": ["creative studio space", "morning journaling", "collaborative workshops"],
            "core_values": ["authentic expression", "gentle growth", "creative freedom"],
            "energy_vibe": "flowing creative energy",
            "visual_style": "organic and handcrafted"
        }
        
        # Creative intake answers
        creative_intake_answers = {
            "1": {
                "answer": "I want to feel deeply connected to my creative flow, like every brushstroke has meaning.",
                "theme": "creative_fulfillment",
                "timestamp": "2024-01-15T09:00:00"
            },
            "2": {
                "answer": "I want to be known for creating art that helps people find their own creative voice.",
                "theme": "legacy_vision",
                "timestamp": "2024-01-15T09:01:00"
            },
            "3": {
                "answer": "I'm learning hand-lettering and calligraphy to add personal touches to everything I create.",
                "theme": "skill_development",
                "timestamp": "2024-01-15T09:02:00"
            },
            "4": {
                "answer": "Taking care of myself means morning pages, afternoon walks, and evening tea rituals.",
                "theme": "self_care",
                "timestamp": "2024-01-15T09:03:00"
            },
            "5": {
                "answer": "I want to surround myself with other creative souls who believe in handmade beauty.",
                "theme": "relationships",
                "timestamp": "2024-01-15T09:04:00"
            }
        }
        
        print("✍️ Test 1: Creative Layout & Handwriting Generation")
        print("-" * 60)
        enhanced_prompt = vision_generator.create_enhanced_llm_prompt(creative_artist_persona, creative_intake_answers)
        
        if enhanced_prompt:
            print(f"✅ Creative enhanced prompt generated successfully!")
            print(f"📏 Prompt length: {len(enhanced_prompt)} characters")
            
            # Test for handwriting elements
            handwriting_keywords = [
                "handwriting", "hand-lettered", "handwritten", "calligraphy", 
                "script", "hand-drawn", "flowing script", "elegant script"
            ]
            handwriting_found = sum(1 for keyword in handwriting_keywords if keyword.lower() in enhanced_prompt.lower())
            print(f"✍️ Handwriting elements: {handwriting_found}/{len(handwriting_keywords)} found")
            
            if handwriting_found >= 3:
                print("✅ Strong handwriting integration detected")
            else:
                print("⚠️ Limited handwriting elements found")
            
            # Test for creative layout elements
            creative_layout_keywords = [
                "organic shapes", "flowing curves", "creative shapes", "hexagon", "circle",
                "flowing", "organic", "creative freedom", "asymmetrical", "dynamic"
            ]
            layout_found = sum(1 for keyword in creative_layout_keywords if keyword.lower() in enhanced_prompt.lower())
            print(f"🎨 Creative layout elements: {layout_found}/{len(creative_layout_keywords)} found")
            
            if layout_found >= 5:
                print("✅ Strong creative layout integration detected")
            else:
                print("⚠️ Limited creative layout elements found")
            
            # Test for mixed media mentions
            mixed_media_keywords = [
                "mixed media", "photography", "typography", "handwriting", "texture",
                "natural", "contemporary", "magazine", "modern"
            ]
            media_found = sum(1 for keyword in mixed_media_keywords if keyword.lower() in enhanced_prompt.lower())
            print(f"🎭 Mixed media elements: {media_found}/{len(mixed_media_keywords)} found")
            
            # Test for personal touch elements
            personal_keywords = [
                "actual words", "personal", "authentic", "meaningful", "their", "user's"
            ]
            personal_found = sum(1 for keyword in personal_keywords if keyword.lower() in enhanced_prompt.lower())
            print(f"❤️ Personal touch elements: {personal_found}/{len(personal_keywords)} found")
            
            print()
            print("✍️ SAMPLE OF CREATIVE ENHANCED PROMPT:")
            print("-" * 60)
            # Show specific sections that demonstrate creativity
            lines = enhanced_prompt.split('\n')
            creative_sections = []
            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in handwriting_keywords + creative_layout_keywords):
                    creative_sections.append(line.strip())
            
            for section in creative_sections[:8]:  # Show first 8 relevant lines
                print(f"• {section}")
            
            if len(creative_sections) > 8:
                print("... and more creative elements")
            
            print()
            
        else:
            print("❌ Creative enhanced prompt generation failed")
            return False
            
        print("✍️ Test 2: Magazine vs Museum Style Verification")
        print("-" * 60)
        
        # Check that it's magazine-focused, not museum-focused
        museum_words = ["museum", "gallery", "masterpiece", "fine art", "archaeological"]
        magazine_words = ["magazine", "instagram", "pinterest", "lifestyle", "contemporary", "trendy"]
        
        museum_count = sum(1 for word in museum_words if word.lower() in enhanced_prompt.lower())
        magazine_count = sum(1 for word in magazine_words if word.lower() in enhanced_prompt.lower())
        
        print(f"📰 Magazine style mentions: {magazine_count}")
        print(f"🏛️ Museum style mentions: {museum_count}")
        
        if magazine_count > museum_count:
            print("✅ Successfully focused on modern magazine aesthetic")
        else:
            print("⚠️ Still has museum-style language")
            
        print()
        print("✍️ Test 3: Creative Freedom Assessment")
        print("-" * 60)
        
        # Test for creative freedom indicators
        freedom_indicators = [
            "creative freedom", "break traditional", "organic", "flowing", 
            "dynamic", "creative boundaries", "authentic", "personal"
        ]
        
        freedom_found = sum(1 for indicator in freedom_indicators if indicator.lower() in enhanced_prompt.lower())
        print(f"🎨 Creative freedom indicators: {freedom_found}/{len(freedom_indicators)}")
        
        if freedom_found >= 4:
            print("✅ High creative freedom encouraged")
        else:
            print("⚠️ Limited creative freedom detected")
        
        print()
        print("🎯 OVERALL CREATIVE ASSESSMENT:")
        print("=" * 60)
        
        total_score = handwriting_found + layout_found + media_found + personal_found + freedom_found
        max_score = len(handwriting_keywords) + len(creative_layout_keywords) + len(mixed_media_keywords) + len(personal_keywords) + len(freedom_indicators)
        
        percentage = (total_score / max_score) * 100
        
        print(f"✍️ Handwriting Integration: {'✅ EXCELLENT' if handwriting_found >= 3 else '⚠️ NEEDS IMPROVEMENT'}")
        print(f"🎨 Creative Layouts: {'✅ EXCELLENT' if layout_found >= 5 else '⚠️ NEEDS IMPROVEMENT'}")
        print(f"🎭 Mixed Media: {'✅ EXCELLENT' if media_found >= 5 else '⚠️ GOOD'}")
        print(f"❤️ Personal Touch: {'✅ EXCELLENT' if personal_found >= 3 else '⚠️ GOOD'}")
        print(f"🆓 Creative Freedom: {'✅ EXCELLENT' if freedom_found >= 4 else '⚠️ GOOD'}")
        print(f"📰 Magazine Style: {'✅ MODERN' if magazine_count > museum_count else '⚠️ TRADITIONAL'}")
        print()
        print(f"📊 Overall Creative Score: {percentage:.1f}%")
        
        if percentage >= 70:
            print("🏆 EXCELLENT CREATIVE VISION BOARD SYSTEM!")
            print("✍️ Ready to create stunning handwritten, creative layouts")
        elif percentage >= 50:
            print("✅ GOOD CREATIVE SYSTEM")
            print("✍️ Strong foundation with room for enhancement")
        else:
            print("⚠️ NEEDS CREATIVE IMPROVEMENT")
            print("✍️ Consider adding more handwriting and layout flexibility")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during creative testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_creative_handwriting_features()
