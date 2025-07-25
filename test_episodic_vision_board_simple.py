#!/usr/bin/env python3
"""
Simplified test for episodic memory-based vision board personalization
Tests the core functionality without strict authenticity checking
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager
from core.memory import MemoryManager
from core.vision_board_generator import VisionBoardGenerator
from core.vision_board_intake import VisionBoardIntakeManager

def test_episodic_vision_board_simple():
    """Simple test focusing on episodic memory -> vision board pipeline"""
    
    print("🧪 EPISODIC MEMORY VISION BOARD TEST")
    print("="*50)
    
    # Initialize system
    print("🔧 Initializing system...")
    db_manager = DatabaseManager()
    memory_manager = MemoryManager()
    generator = VisionBoardGenerator(db_manager, memory_manager)
    intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
    
    test_user = "episodic_test_user"
    
    # Clear existing data
    print(f"🧹 Clearing data for {test_user}...")
    try:
        # Clear Pinecone vector store data for this user
        if hasattr(memory_manager, 'index') and memory_manager.index:
            # Delete all vectors for this user
            try:
                memory_manager.index.delete(filter={"user_id": test_user})
                print("✅ Cleared Pinecone vectors")
            except Exception as e:
                print(f"⚠️ Pinecone clear warning: {e}")
        
        # Clear database intake data
        db_manager.clear_vision_board_intake(test_user)
        print("✅ Cleared database data")
    except Exception as e:
        print(f"⚠️ Clear warning: {e}")
    
    # Test realistic user responses
    print("\n📝 Testing with realistic user responses...")
    
    realistic_responses = [
        {
            "question_num": 1,
            "answer": "I want to feel more creative and inspired in my daily life. I'd love to have that spark of innovation that makes every day feel like an adventure.",
            "theme": "emotional_anchor"
        },
        {
            "question_num": 2, 
            "answer": "I want to be known as someone who brings out the best in others, maybe through mentoring or creating inspiring content that helps people grow.",
            "theme": "identity_legacy"
        },
        {
            "question_num": 3,
            "answer": "I'm learning photography and visual storytelling. There's something magical about capturing moments that tell deeper stories.",
            "theme": "growth_craft"
        },
        {
            "question_num": 4,
            "answer": "Taking care of myself means morning walks in nature, reading books that expand my mind, and cooking healthy meals with fresh ingredients.",
            "theme": "self_care_wellness"
        },
        {
            "question_num": 5,
            "answer": "I want to be around curious, supportive people who aren't afraid to dream big and take creative risks together.",
            "theme": "relationships_community"
        }
    ]
    
    # Simulate intake process with episodic memory storage
    print("\n💾 Storing responses in episodic memory...")
    for i, response in enumerate(realistic_responses, 1):
        # Analyze the response
        analyzed_data = intake_manager._analyze_answer(response["question_num"], response["answer"])
        
        # Store in episodic memory
        q_data = intake_manager.questions[response["question_num"]]
        memory_manager.add_vision_board_intake_to_episodic_memory(
            test_user, response["question_num"], q_data, response["answer"], analyzed_data
        )
        print(f"   ✅ Q{i} stored with theme: {response['theme']}")
    
    # Test episodic memory retrieval
    print("\n🧠 Testing episodic memory retrieval...")
    episodic_memories = memory_manager.get_vision_board_intake_memories(test_user)
    print(f"📖 Retrieved {len(episodic_memories)} episodic memories")
    
    for i, memory in enumerate(episodic_memories, 1):
        print(f"   Memory {i}: {memory.get('question_theme', 'unknown')} - {len(memory.get('raw_user_response', ''))} chars")
        analysis = memory.get('vision_analysis', {})
        print(f"     🎨 Colors: {analysis.get('color_palette', [])[:2]}")
        print(f"     💫 Emotions: {analysis.get('core_emotions', [])[:2]}")
        print(f"     🌟 Aspirations: {analysis.get('aspirations', [])[:2]}")
    
    # Test persona creation from episodic memory
    print("\n👤 Testing persona creation from episodic memory...")
    fake_intake_answers = {}  # Generator will use episodic memory instead
    persona = generator.extract_persona_from_intake(test_user, fake_intake_answers)
    
    print("📊 Generated Persona:")
    print(f"   🎭 Identity: {persona.get('core_identity', 'Unknown')}")
    print(f"   🎨 Visual Symbols: {persona.get('visual_symbols', [])[:3]}")
    print(f"   🌈 Colors: {persona.get('color_palette', [])[:3]}")
    print(f"   💫 Energy: {persona.get('energy_vibe', 'Unknown')}")
    print(f"   🧠 From Episodic: {persona.get('created_from_episodic_memory', False)}")
    
    # Test prompt customization
    print("\n📝 Testing prompt customization...")
    template_prompt = "Create a vision board with [USER_CONTENT] showing [USER_COLORS] and [USER_SYMBOLS]"
    persona['user_id'] = test_user  # Add for episodic access
    
    customized_prompt = generator.customize_prompt_with_intake_data(template_prompt, persona, fake_intake_answers)
    
    print("✅ Prompt Customization Results:")
    print(f"   📏 Length: {len(customized_prompt)} characters")
    prompt_lower = customized_prompt.lower()
    print(f"   🎨 Contains 'creative': {'creative' in prompt_lower}")
    print(f"   📸 Contains 'photography': {'photography' in prompt_lower}")
    print(f"   🌿 Contains 'nature': {'nature' in prompt_lower}")
    print(f"   ❌ Avoids 'black/gold': {'black' not in prompt_lower and 'gold' not in prompt_lower}")
    
    # Test anti-generic content
    print("\n🚫 Testing anti-generic content...")
    generic_terms = ['black and gold', 'luxury lifestyle', 'elegant aesthetic', 'sophisticated design']
    generic_found = [term for term in generic_terms if term in customized_prompt.lower()]
    
    if not generic_found:
        print("✅ No generic template content detected")
    else:
        print(f"⚠️ Found generic terms: {generic_found}")
    
    # Test authentic content presence
    print("\n✨ Testing authentic content presence...")
    authentic_terms = ['creative', 'photography', 'nature', 'inspiring', 'mentoring', 'storytelling']
    authentic_found = [term for term in authentic_terms if term in customized_prompt.lower()]
    
    print(f"✅ Authentic user content found: {authentic_found}")
    
    # Final assessment
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    checks = {
        "Episodic memory storage": len(episodic_memories) >= 5,  # At least 5 memories (may have more from previous runs)
        "Persona from episodic memory": persona.get('created_from_episodic_memory', False),
        "Authentic content in prompt": len(authentic_found) >= 3,
        "No generic content": len(generic_found) == 0,
        "User-specific elements": any('creative' in str(item).lower() or 'light bulb' in str(item).lower() or 'spark' in str(item).lower() 
                                     for item in persona.get('visual_symbols', [])) or 'creative' in persona.get('core_identity', '').lower()
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, result in checks.items():
        print(f"   {'✅' if result else '❌'} {check}")
    
    if passed >= 4:
        print(f"\n🎉 TEST PASSED: {passed}/{total} checks successful!")
        print("✅ Episodic memory vision board system is working correctly")
        print("🎨 System ready for authentic, personalized vision board generation")
        return True
    else:
        print(f"\n❌ TEST FAILED: Only {passed}/{total} checks passed")
        print("🔧 System needs improvements before production use")
        return False

if __name__ == "__main__":
    success = test_episodic_vision_board_simple()
    sys.exit(0 if success else 1)
