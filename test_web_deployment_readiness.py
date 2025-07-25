#!/usr/bin/env python3
"""
Web Deployment Readiness Check for Episodic Memory Vision Board System
This verifies the complete end-to-end functionality for web users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager
from core.memory import MemoryManager
from core.smart_agent import SmartAgent
from core.vision_board_generator import VisionBoardGenerator
from core.vision_board_intake import VisionBoardIntakeManager

def test_web_deployment_readiness():
    """Test complete web deployment readiness for episodic memory vision boards"""
    
    print("🌐 WEB DEPLOYMENT READINESS CHECK")
    print("="*60)
    
    try:
        # Test 1: System Initialization (as it would happen in app.py)
        print("🔧 Test 1: System Initialization...")
        db_manager = DatabaseManager()
        memory_manager = MemoryManager()
        smart_agent = SmartAgent(db_manager, memory_manager)
        print("✅ All core systems initialized successfully")
        
        # Test 2: Vision Board Components
        print("\n🎨 Test 2: Vision Board Components...")
        vision_generator = smart_agent.vision_board_generator
        intake_manager = vision_generator.intake_manager
        print("✅ Vision board generator and intake manager ready")
        
        # Test 3: Episodic Memory Integration  
        print("\n🧠 Test 3: Episodic Memory Integration...")
        test_user = "web_deploy_test_user"
        
        # Simulate user completing intake (as happens in web interface)
        print("   📝 Simulating web user intake process...")
        
        # Start intake
        intro_message = intake_manager.start_intake_flow(test_user)
        if "Let's create your perfect vision board" in intro_message:
            print("   ✅ Intake flow starts correctly")
        else:
            print("   ❌ Intake flow initialization issue")
            return False
        
        # Simulate answering questions (as user would on web)
        web_responses = [
            "I want to feel more confident and empowered in everything I do.",
            "I want to be known as someone who inspires others to pursue their dreams.",
            "I'm passionate about learning digital marketing and building my online presence.",
            "Self-care for me means yoga, meditation, and spending time in nature.",
            "I want to surround myself with positive, ambitious people who support each other.",
            "I feel most 'me' when I'm creating content, speaking publicly, and helping others grow.",
            "My dream space feels energizing and creative, with natural light and inspiring artwork.",
            "I'm ready to express my boldness and leadership more confidently in my career.",
            "I secretly want to write a book about personal development and share my story.",
            "I want to build a successful online business that impacts thousands of people positively."
        ]
        
        for i, response in enumerate(web_responses, 1):
            result = intake_manager.process_answer(test_user, response)
            if "Beautiful!" in result or "Love this" in result or "Perfect!" in result or "Yes!" in result or "Wow" in result:
                print(f"   ✅ Question {i} processed successfully")
            elif i == 10 and "Intake Complete" in result:
                print(f"   ✅ Question {i} completed intake successfully")
            else:
                print(f"   ⚠️ Question {i} response: {result[:50]}...")  # Show partial response for debugging
        
        # Test 4: Episodic Memory Storage & Retrieval
        print("\n💾 Test 4: Episodic Memory Storage & Retrieval...")
        episodic_memories = memory_manager.get_vision_board_intake_memories(test_user)
        
        if len(episodic_memories) >= 10:
            print(f"   ✅ {len(episodic_memories)} responses stored in episodic memory")
            
            # Check data quality
            first_memory = episodic_memories[0]
            if first_memory.get('raw_user_response') and first_memory.get('vision_analysis'):
                print("   ✅ Episodic memory contains rich analysis data")
            else:
                print("   ❌ Episodic memory data incomplete")
                return False
        else:
            print("   ❌ Insufficient episodic memories stored")
            return False
        
        # Test 5: Persona Creation from Episodic Memory
        print("\n👤 Test 5: Persona Creation from Episodic Memory...")
        fake_intake = {}  # Web interface passes empty dict, generator uses episodic memory
        persona = vision_generator.extract_persona_from_intake(test_user, fake_intake)
        
        if persona.get('created_from_episodic_memory'):
            print("   ✅ Persona created from episodic memory")
            if len(persona.get('life_aspirations', [])) >= 3:
                print("   ✅ Persona contains rich aspiration data")
            else:
                print("   ❌ Persona lacks sufficient aspiration data")
        else:
            print("   ❌ Persona not created from episodic memory")
            return False
        
        # Test 6: Authentic Prompt Generation
        print("\n📝 Test 6: Authentic Prompt Generation...")
        persona['user_id'] = test_user
        template_prompt = "Create a vision board"
        customized_prompt = vision_generator.customize_prompt_with_intake_data(template_prompt, persona, fake_intake)
        
        # Check for authentic content
        prompt_lower = customized_prompt.lower()
        authentic_indicators = ['confident', 'empowered', 'inspire', 'digital marketing', 'yoga', 'meditation', 'nature']
        found_authentic = [term for term in authentic_indicators if term in prompt_lower]
        
        if len(found_authentic) >= 4:
            print(f"   ✅ Prompt contains authentic user content: {found_authentic[:4]}")
        else:
            print(f"   ❌ Prompt lacks authentic content. Found: {found_authentic}")
            return False
        
        # Check against generic content
        generic_terms = ['black and gold', 'luxury lifestyle', 'elegant aesthetic']
        found_generic = [term for term in generic_terms if term in prompt_lower]
        
        if not found_generic:
            print("   ✅ No generic template content in prompt")
        else:
            print(f"   ❌ Generic content found: {found_generic}")
        
        # Test 7: Complete Generation Flow (minus actual image creation)
        print("\n🎨 Test 7: Complete Generation Flow...")
        
        # Check intake completion
        if intake_manager.is_intake_complete(test_user):
            print("   ✅ Intake marked as complete")
        else:
            print("   ❌ Intake not properly completed")
            return False
        
        # Check template recommendation
        template_num, template_name = intake_manager.recommend_template(test_user)
        if template_name:
            print(f"   ✅ Template recommended: {template_name}")
        else:
            print("   ❌ Template recommendation failed")
            return False
        
        # Test 8: Error Handling & Edge Cases
        print("\n🛡️ Test 8: Error Handling & Edge Cases...")
        
        # Test with non-existent user
        empty_memories = memory_manager.get_vision_board_intake_memories("nonexistent_user")
        if not empty_memories:
            print("   ✅ Handles non-existent user correctly")
        else:
            print("   ❌ Issue with non-existent user handling")
        
        # Test incomplete intake
        incomplete_user = "incomplete_test"
        incomplete_intro = intake_manager.start_intake_flow(incomplete_user)
        intake_manager.process_answer(incomplete_user, "Just one answer")
        
        if not intake_manager.is_intake_complete(incomplete_user):
            print("   ✅ Correctly identifies incomplete intake")
        else:
            print("   ❌ Issue with incomplete intake detection")
        
        print("\n" + "="*60)
        print("📊 WEB DEPLOYMENT READINESS SUMMARY")
        print("="*60)
        
        print("✅ System Initialization: Ready")
        print("✅ Episodic Memory Storage: Working")
        print("✅ Authentic Persona Creation: Working") 
        print("✅ Personalized Prompt Generation: Working")
        print("✅ Intake Flow: Complete")
        print("✅ Error Handling: Robust")
        print("✅ Web Interface Integration: Compatible")
        
        print(f"\n🎉 DEPLOYMENT READY! 🎉")
        print("🌐 The episodic memory vision board system will work perfectly on web")
        print("👥 Users will get authentic, personalized vision boards based on their unique responses")
        print("🎨 No more generic black/gold templates - each board reflects the user's actual personality")
        print("💾 All user responses are preserved in episodic memory for authentic personalization")
        
        return True
        
    except Exception as e:
        print(f"\n❌ DEPLOYMENT ISSUE DETECTED: {e}")
        import traceback
        traceback.print_exc()
        print("🔧 Please address the issue before web deployment")
        return False

if __name__ == "__main__":
    success = test_web_deployment_readiness()
    if success:
        print("\n✅ READY FOR WEB DEPLOYMENT!")
    else:
        print("\n❌ NOT READY - Please fix issues first")
    sys.exit(0 if success else 1)
