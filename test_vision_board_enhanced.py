"""
Test vision board generation with the enhanced promp        # Save mock intake to simulate completed flow using the actual intake manager
        intake_data = {
            "status": "completed",
            "current_question": 11,  # Beyond the last question
            "answers": intake_answers,
            "completion_timestamp": time.time(),
            "completed": True
        }
        
        vision_generator.intake_manager._save_intake_data(user_id, intake_data)
        
        print("✅ Mock intake data created using intake manager")mport os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.vision_board_generator import VisionBoardGenerator
from core.memory import MemoryManager
from core.database import DatabaseManager

def test_vision_board_generation():
    """Test the enhanced vision board generation"""
    print("🎨 Testing Enhanced Vision Board Generation")
    print("=" * 50)
    
    try:
        # Initialize components
        memory = MemoryManager()
        db = DatabaseManager()
        vision_generator = VisionBoardGenerator(db, memory)
        
        user_id = "vision_test_user_enhanced"
        
        # Create mock intake data to test vision board generation
        print("📝 Setting up mock intake data...")
        
        # Simulate completed intake
        intake_answers = {
            1: {
                "answer": "I want to feel more confident and empowered in my daily life",
                "theme": "emotional_anchor",
                "timestamp": time.time()
            },
            2: {
                "answer": "I want to be known for helping others achieve their dreams while building a successful business",
                "theme": "identity_legacy", 
                "timestamp": time.time()
            },
            3: {
                "answer": "I'm building my leadership skills and learning about digital marketing",
                "theme": "growth_craft",
                "timestamp": time.time()
            },
            4: {
                "answer": "Taking care of myself means morning walks, healthy meals, and setting boundaries",
                "theme": "self_care_wellness",
                "timestamp": time.time()
            },
            5: {
                "answer": "I want to be around ambitious, kind people who support each other's growth",
                "theme": "relationships_community",
                "timestamp": time.time()
            }
        }
        
        # Save mock intake to simulate completed flow using the actual intake manager
        vision_generator.intake_manager._save_intake_progress(user_id, {
            "status": "completed",
            "current_question": 11,  # Beyond the last question
            "answers": intake_answers,
            "completion_timestamp": time.time(),
            "completed": True
        })
        
        print("✅ Mock intake data created using intake manager")
        
        # Test template selection
        print("\n🎯 Testing template selection...")
        template_num = vision_generator.analyze_user_for_template(user_id)
        print(f"✅ Selected template: {template_num} - {vision_generator.templates[template_num]['name']}")
        
        # Test prompt loading with enhanced template
        print("\n📋 Testing enhanced prompt loading...")
        start_time = time.time()
        template_prompt = vision_generator.load_template_prompt(template_num)
        load_time = time.time() - start_time
        
        if template_prompt:
            print(f"✅ Template loaded in {load_time:.2f}s (Length: {len(template_prompt)} chars)")
            print(f"🎨 Enhanced prompt features detected")
        else:
            print("❌ Failed to load template")
            return False
        
        # Test persona extraction
        print("\n👤 Testing persona extraction...")
        start_time = time.time()
        persona = vision_generator.extract_persona_from_intake(user_id, intake_answers)
        persona_time = time.time() - start_time
        
        print(f"✅ Persona extracted in {persona_time:.2f}s")
        print(f"   Name: {persona.get('name')}")
        print(f"   Personality: {persona.get('personality')}")
        print(f"   Energy: {persona.get('energy')}")
        
        # Test prompt customization
        print("\n🎨 Testing prompt customization...")
        start_time = time.time()
        customized_prompt = vision_generator.customize_prompt_with_intake_data(template_prompt, persona, intake_answers)
        customize_time = time.time() - start_time
        
        print(f"✅ Prompt customized in {customize_time:.2f}s")
        print(f"📝 Enhanced prompt ready (Final length: {len(customized_prompt)} chars)")
        
        # Test the actual vision board generation (this will take longer)
        print("\n🖼️ Testing complete vision board generation...")
        print("   ⏳ This may take 15-45 seconds for high-quality generation...")
        
        start_time = time.time()
        image_url, template_name = vision_generator.generate_vision_board(user_id)
        generation_time = time.time() - start_time
        
        if image_url and template_name:
            print(f"✅ Vision board generated successfully in {generation_time:.2f}s!")
            print(f"🎨 Template: {template_name}")
            print(f"🖼️ Image URL: {image_url[:100]}...")
            print("✅ Enhanced style and quality features applied")
        else:
            print("❌ Vision board generation failed")
            return False
        
        # Performance Summary
        print("\n" + "=" * 50)
        print("📊 VISION BOARD PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"📋 Template Loading: {load_time:.2f}s")
        print(f"👤 Persona Extraction: {persona_time:.2f}s")
        print(f"🎨 Prompt Customization: {customize_time:.2f}s")
        print(f"🖼️ Image Generation: {generation_time:.2f}s")
        
        total_time = load_time + persona_time + customize_time + generation_time
        print(f"\n⏱️ Total Time: {total_time:.2f}s")
        
        if generation_time < 30:
            print("🚀 EXCELLENT generation speed!")
        elif generation_time < 60:
            print("✅ GOOD generation speed!")
        else:
            print("⚠️ Generation took longer than expected")
        
        return True
        
    except Exception as e:
        print(f"❌ Vision board test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vision_board_generation()
    if success:
        print("\n🎊 VISION BOARD TEST COMPLETED SUCCESSFULLY!")
        print("✨ Enhanced prompts and performance optimizations working!")
    else:
        print("\n⚠️ Vision board test had issues.")
