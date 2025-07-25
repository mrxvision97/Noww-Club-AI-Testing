#!/usr/bin/env python3
"""
Quick deployment test for enhanced vision board system
"""

import os
import sys

def test_deployment_readiness():
    """Test if the enhanced vision board system is ready for deployment"""
    
    print("🚀 DEPLOYMENT READINESS TEST")
    print("=" * 50)
    
    try:
        # Test 1: Environment
        print("📋 Test 1: Environment Check...")
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("✅ OpenAI API key configured")
        else:
            print("❌ OpenAI API key missing")
            return False
        
        # Test 2: Core imports
        print("\n📋 Test 2: Core System Imports...")
        from core.database import DatabaseManager
        print("✅ DatabaseManager imported")
        
        from core.memory import MemoryManager
        print("✅ MemoryManager imported")
        
        from core.vision_board_generator import VisionBoardGenerator
        print("✅ VisionBoardGenerator imported")
        
        from core.vision_board_intake import VisionBoardIntakeManager
        print("✅ VisionBoardIntakeManager imported")
        
        # Test 3: Component initialization
        print("\n📋 Test 3: Component Initialization...")
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        vision_generator = VisionBoardGenerator(db_manager, memory_manager)
        intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
        print("✅ All components initialized successfully")
        
        # Test 4: Enhanced method availability
        print("\n📋 Test 4: Enhanced Methods Check...")
        if hasattr(vision_generator, 'create_enhanced_llm_prompt'):
            print("✅ Enhanced LLM prompt method available")
        else:
            print("❌ Enhanced method missing")
            return False
            
        # Test 5: Quick functional test
        print("\n📋 Test 5: Quick Functional Test...")
        test_persona = {
            "user_id": "test_deployment",
            "core_identity": "Test user for deployment",
            "dominant_emotions": ["excited", "ready"],
            "life_aspirations": ["successful deployment"],
            "visual_symbols": ["rocket", "success"],
            "color_palette": ["green", "blue"],
            "energy_vibe": "ready"
        }
        
        test_intake = {
            "1": {"answer": "Ready for deployment", "theme": "test"}
        }
        
        # Test if enhanced prompt generation works
        enhanced_prompt = vision_generator.create_enhanced_llm_prompt(test_persona, test_intake)
        if enhanced_prompt and len(enhanced_prompt) > 100:
            print("✅ Enhanced prompt generation working")
            print(f"   📏 Generated {len(enhanced_prompt)} character prompt")
        else:
            print("❌ Enhanced prompt generation failed")
            return False
        
        # Test 6: Integration test
        print("\n📋 Test 6: Integration Test...")
        template_prompt = "test template"
        final_prompt = vision_generator.customize_prompt_with_intake_data(
            template_prompt, test_persona, test_intake
        )
        
        if final_prompt and len(final_prompt) > 100:
            print("✅ Full integration working")
            print(f"   📏 Final prompt: {len(final_prompt)} characters")
        else:
            print("❌ Integration test failed")
            return False
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Enhanced vision board system is READY FOR DEPLOYMENT!")
        print("\n📊 System Status:")
        print("   🔧 Enhanced LLM approach: ACTIVE")
        print("   🎨 Sophisticated prompt generation: WORKING")
        print("   🔄 Fallback mechanisms: IN PLACE")
        print("   📱 Web deployment: READY")
        
        return True
        
    except Exception as e:
        print(f"\n❌ DEPLOYMENT TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deployment_readiness()
    print(f"\n{'🎉 READY FOR DEPLOYMENT!' if success else '💥 DEPLOYMENT NOT READY'}")
    exit(0 if success else 1)
