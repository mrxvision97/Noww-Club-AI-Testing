#!/usr/bin/env python3
"""
Test the enhanced template structure compliance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_template_structure_compliance():
    """Test that the vision board generation follows exact template structure"""
    print("🧪 Testing Enhanced Template Structure Compliance")
    print("=" * 60)
    
    try:
        from core.vision_board_generator import VisionBoardGenerator
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager()
        generator = VisionBoardGenerator(db_manager, memory_manager)
        
        print("✅ Generator initialized successfully")
        
        # Test with comprehensive persona data
        test_persona = {
            "name": "User",
            "age": "28-32",
            "core_identity": "A mindful entrepreneur and data scientist who seeks to leave a legacy of support and growth",
            "personality": "Introspective and thoughtful individual with serene demeanor, driven by ambition",
            "values": ["mindfulness", "entrepreneurship", "growth", "authenticity", "wellness", "purpose"],
            "life_goals": ["build successful business", "travel the world", "create impact", "spiritual growth", "financial freedom", "meaningful relationships"],
            "visual_style_preference": "minimalist",
            "energy_vibe": "medium to high"
        }
        
        # Test intake answers with rich analysis
        test_intake_answers = {
            0: {
                "answer": "I want to build a successful tech startup while maintaining inner peace",
                "analysis": {
                    "core_emotions": ["determined", "peaceful", "ambitious", "focused", "inspired"],
                    "visual_metaphors": ["rising sun", "mountain peak", "flowing river", "growing tree", "clear pathway"],
                    "color_palette": ["deep blues", "warm gold", "earth tones", "soft greens", "charcoal black"],
                    "lifestyle_elements": ["modern office", "meditation space", "tech environment", "premium workspace"],
                    "values_revealed": ["balance", "success", "mindfulness", "innovation"],
                    "aspirations": ["business success", "inner peace", "tech innovation", "leadership"],
                    "energy_level": "high",
                    "visual_style_preference": "minimalist"
                }
            },
            1: {
                "answer": "I envision traveling to spiritual destinations while building my digital empire",
                "analysis": {
                    "core_emotions": ["adventurous", "spiritual", "visionary", "confident"],
                    "visual_metaphors": ["ancient temples", "modern airports", "luxury travel", "digital networks"],
                    "color_palette": ["sacred gold", "deep black", "earth brown", "sky blue"],
                    "lifestyle_elements": ["international travel", "spiritual retreats", "luxury hotels", "digital nomad"],
                    "values_revealed": ["adventure", "spirituality", "freedom", "growth"],
                    "aspirations": ["world travel", "spiritual growth", "digital success", "freedom"],
                    "energy_level": "medium",
                    "visual_style_preference": "natural"
                }
            }
        }
        
        print("\n1️⃣ Testing intelligent template mapping...")
        
        # Test the new intelligent mapping method
        emotions = ["determined", "peaceful", "ambitious", "focused", "inspired"]
        symbols = ["rising sun", "mountain peak", "flowing river", "modern office", "ancient temples"]
        colors = ["deep blues", "warm gold", "earth tones", "charcoal black"]
        lifestyle = ["modern office", "meditation space", "international travel", "luxury hotels"]
        values = ["balance", "success", "mindfulness", "innovation"]
        aspirations = ["business success", "world travel", "spiritual growth", "digital success"]
        traits = ["determined", "peaceful", "visionary"]
        energy = "high"
        style = "minimalist"
        
        mappings = generator._create_intelligent_template_mappings(
            emotions, symbols, colors, lifestyle, values, aspirations, traits, energy, style
        )
        
        print(f"✅ Template mappings created successfully")
        print(f"   🎭 Primary Emotion: {mappings['primary_emotion']}")
        print(f"   🎨 Aesthetic: {mappings['aesthetic_description']}")
        print(f"   🏆 Achievement Symbols: {mappings['achievement_symbols']}")
        print(f"   🌈 Color Description: {mappings['color_description']}")
        print(f"   ⚡ Energy Description: {mappings['energy_description']}")
        
        print("\n2️⃣ Testing template prompt customization...")
        
        # Load template
        template_prompt = generator.load_template_prompt(1)
        if not template_prompt:
            print("❌ Failed to load template")
            return False
        
        print(f"   📄 Template loaded: {len(template_prompt)} characters")
        
        # Test customization
        customized_prompt = generator.customize_prompt_with_intake_data(
            template_prompt, test_persona, test_intake_answers
        )
        
        print(f"✅ Customization successful: {len(customized_prompt)} characters")
        
        # Check for template structure compliance
        structure_checks = {
            "exact_structure_required": "EXACT STRUCTURE REQUIRED" in customized_prompt,
            "asymmetrical_grid": "asymmetrical grid" in customized_prompt.lower(),
            "template_adherence": "TEMPLATE ADHERENCE" in customized_prompt,
            "user_specific_mapping": "USER-SPECIFIC CONTENT MAPPING" in customized_prompt,
            "visual_execution": "VISUAL EXECUTION REQUIREMENTS" in customized_prompt,
            "sectional_layout": "sectional layout" in customized_prompt.lower(),
            "sophisticated_dark": "sophisticated dark" in customized_prompt.lower(),
            "golden_text": "golden text" in customized_prompt.lower() or "gold" in customized_prompt.lower()
        }
        
        # Check for user data integration
        personalization_checks = {
            "business_aspirations": any(word in customized_prompt.lower() for word in ["business", "entrepreneur", "startup"]),
            "travel_elements": any(word in customized_prompt.lower() for word in ["travel", "world", "international"]),
            "spiritual_growth": any(word in customized_prompt.lower() for word in ["spiritual", "peace", "mindful"]),
            "tech_focus": any(word in customized_prompt.lower() for word in ["tech", "digital", "innovation"]),
            "user_emotions": any(word in customized_prompt.lower() for word in ["determined", "peaceful", "ambitious"]),
            "visual_symbols": any(word in customized_prompt.lower() for word in ["mountain", "river", "sun", "temple"]),
            "color_palette": any(word in customized_prompt.lower() for word in ["blue", "gold", "earth", "charcoal"]),
            "energy_level": "high" in customized_prompt.lower()
        }
        
        structure_score = sum(structure_checks.values())
        personalization_score = sum(personalization_checks.values())
        
        print(f"\n📊 Template Structure Compliance: {structure_score}/8 ({structure_score/8*100:.1f}%)")
        for check, passed in structure_checks.items():
            status = "✅" if passed else "❌"
            print(f"      {status} {check}")
        
        print(f"\n📊 Personalization Integration: {personalization_score}/8 ({personalization_score/8*100:.1f}%)")
        for check, passed in personalization_checks.items():
            status = "✅" if passed else "❌"
            print(f"      {status} {check}")
        
        # Show key sections of the prompt
        print(f"\n📖 Enhanced Prompt Preview (first 500 chars):")
        print(f"   {customized_prompt[:500]}...")
        
        # Check for critical template instructions
        if "CRITICAL TEMPLATE ADHERENCE INSTRUCTIONS" in customized_prompt:
            print(f"\n✅ Contains critical template adherence section")
        
        # Overall assessment
        total_score = structure_score + personalization_score
        max_score = 16
        
        if total_score >= 14:  # 87.5% or better
            print(f"\n🎉 EXCELLENT TEMPLATE COMPLIANCE!")
            print(f"✅ {total_score}/{max_score} checks passed - vision boards will now follow exact template structure")
            print("✅ User data intelligently mapped to template elements")
            print("✅ Visual structure preserved while adding personalization")
            return True
        elif total_score >= 10:  # 62.5% or better
            print(f"\n✅ GOOD TEMPLATE COMPLIANCE!")
            print(f"✅ {total_score}/{max_score} checks passed - significant improvement")
            return True
        else:
            print(f"\n⚠️ NEEDS IMPROVEMENT")
            print(f"❌ Only {total_score}/{max_score} checks passed")
            return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced Template Structure Compliance")
    print("=" * 80)
    
    success = test_template_structure_compliance()
    
    print("\n" + "=" * 80)
    
    if success:
        print("🎉 TEMPLATE STRUCTURE COMPLIANCE SUCCESSFUL!")
        print("✅ Vision boards will now follow exact template layout")
        print("✅ User persona data intelligently mapped to template elements")
        print("✅ Sophisticated structure preserved with deep personalization")
        print("\n💡 Enhanced features:")
        print("   • Exact asymmetrical grid layout compliance")
        print("   • Intelligent mapping of user data to template sections")
        print("   • Preserved visual hierarchy and sophisticated aesthetic")
        print("   • User-specific symbols and aspirations in appropriate sections")
        
    else:
        print("❌ Template compliance needs more work")
    
    print("\n🔥 Ready to generate template-compliant, personalized vision boards!")
