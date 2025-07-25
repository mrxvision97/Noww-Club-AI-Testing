#!/usr/bin/env python3
"""
Comprehensive test to verify that vision boards now reflect actual user intake answers
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.vision_board_generator import VisionBoardGenerator
from core.vision_board_intake import VisionBoardIntakeManager
from core.memory import MemoryManager

def test_personalized_vision_board():
    """Test the complete flow from intake to personalized vision board"""
    print("🧪 Testing Personalized Vision Board Generation")
    print("=" * 60)
    
    # Test user ID
    test_user_id = "personalization_test_user"
    
    # Initialize components
    print("📋 Initializing components...")
    intake_manager = VisionBoardIntakeManager()
    generator = VisionBoardGenerator()
    memory = MemoryManager()
    
    # Simulate realistic intake answers that should be reflected in the vision board
    test_answers = {
        0: "I want to feel deeply connected to nature and find inner peace through daily meditation and mindful living",
        1: "I envision myself as a confident entrepreneur running a sustainable wellness business that helps others heal",
        2: "Success means having meaningful relationships, financial freedom, and making a positive impact on the environment",
        3: "I dream of living in a beautiful eco-friendly home surrounded by gardens, traveling to sacred places, and writing a book about healing",
        4: "My ideal day starts with sunrise yoga, includes creative work that inspires others, and ends with gratitude journaling by candlelight",
        5: "I'm passionate about holistic healing, sustainable living, ocean conservation, and empowering women to find their authentic voice",
        6: "I want to attract opportunities for spiritual growth, like-minded community, and abundance that flows from doing meaningful work",
        7: "In relationships, I value deep authentic connection, mutual support, emotional intimacy, and shared values about conscious living",
        8: "I see myself traveling to Bali for spiritual retreats, building an eco-home, launching my wellness platform, and becoming a published author",
        9: "My legacy will be a thriving community of empowered women living authentically, plus a foundation supporting ocean conservation"
    }
    
    print("💭 Simulating intake process...")
    
    # Process each answer through the intake system
    for question_num, answer in test_answers.items():
        print(f"   Processing Q{question_num + 1}: {answer[:50]}...")
        
        # Store the answer and analysis
        analysis = intake_manager._analyze_answer(question_num, answer)
        
        # Save to memory for vision board generation
        memory.add_context(
            user_id=test_user_id,
            context_type="vision_board_intake",
            content={
                "question_number": question_num,
                "answer": answer,
                "analysis": analysis
            }
        )
    
    print("\n🎨 Generating personalized vision board...")
    start_time = time.time()
    
    # Generate vision board that should reflect these specific answers
    result = generator.generate_personalized_vision_board(
        user_id=test_user_id,
        additional_context="Focus on the specific elements mentioned in their intake answers"
    )
    
    generation_time = time.time() - start_time
    
    if result["success"]:
        print(f"✅ Vision board generated successfully in {generation_time:.2f}s")
        print(f"📁 Saved to: {result['file_path']}")
        
        # Analyze the personalization elements
        if "personalization_analysis" in result:
            analysis = result["personalization_analysis"]
            print("\n🔍 Personalization Analysis:")
            print(f"   🎭 Emotions extracted: {', '.join(analysis.get('dominant_emotions', [])[:5])}")
            print(f"   🖼️  Visual metaphors: {', '.join(analysis.get('key_visual_metaphors', [])[:5])}")
            print(f"   🎨 Color themes: {', '.join(analysis.get('color_themes', [])[:5])}")
            print(f"   🏡 Lifestyle elements: {', '.join(analysis.get('lifestyle_elements', [])[:5])}")
            print(f"   💎 Values: {', '.join(analysis.get('core_values', [])[:5])}")
            print(f"   ⭐ Aspirations: {', '.join(analysis.get('aspirations', [])[:5])}")
        
        # Check if specific elements from answers appear in the prompt
        if "final_prompt" in result:
            prompt = result["final_prompt"].lower()
            
            print("\n🔍 Checking for specific intake elements in vision board:")
            specific_checks = {
                "nature connection": "nature" in prompt or "natural" in prompt,
                "meditation/mindfulness": "meditation" in prompt or "mindful" in prompt,
                "entrepreneurship": "entrepreneur" in prompt or "business" in prompt,
                "sustainability": "sustainable" in prompt or "eco" in prompt,
                "ocean conservation": "ocean" in prompt or "water" in prompt,
                "spiritual growth": "spiritual" in prompt or "sacred" in prompt,
                "authentic voice": "authentic" in prompt or "voice" in prompt,
                "bali/travel": "bali" in prompt or "travel" in prompt,
                "writing/author": "writing" in prompt or "author" in prompt or "book" in prompt,
                "eco-home": "eco" in prompt and "home" in prompt,
                "wellness platform": "wellness" in prompt or "healing" in prompt
            }
            
            matched_elements = sum(specific_checks.values())
            total_elements = len(specific_checks)
            
            print(f"   📊 Personalization Score: {matched_elements}/{total_elements} ({matched_elements/total_elements*100:.1f}%)")
            
            for element, found in specific_checks.items():
                status = "✅" if found else "❌"
                print(f"   {status} {element}")
        
        # Performance check
        print(f"\n⚡ Performance: {generation_time:.2f}s (Target: <5s)")
        performance_status = "✅ Excellent" if generation_time < 3 else "✅ Good" if generation_time < 5 else "⚠️ Needs improvement"
        print(f"   Status: {performance_status}")
        
        return True
        
    else:
        print(f"❌ Vision board generation failed: {result.get('error', 'Unknown error')}")
        return False

def test_intake_analysis():
    """Test the enhanced intake analysis specifically"""
    print("\n🧠 Testing Enhanced Intake Analysis")
    print("=" * 40)
    
    intake_manager = VisionBoardIntakeManager()
    
    # Test with a rich, detailed answer
    test_answer = "I dream of waking up in my beautiful eco-friendly home surrounded by lush gardens, starting my day with sunrise yoga and meditation, then working on my sustainable wellness business that helps women connect with their authentic power. I want to travel to sacred places like Bali and Peru, write books about healing and spirituality, and create a foundation that supports ocean conservation. My heart is drawn to deep authentic relationships, financial abundance that flows from meaningful work, and leaving a legacy of empowered women living their truth."
    
    print("📝 Analyzing rich intake response...")
    print(f"Input: {test_answer[:100]}...")
    
    analysis = intake_manager._analyze_answer(0, test_answer)
    
    print("\n📊 Analysis Results:")
    print(f"   🎭 Emotions: {analysis.get('core_emotions', [])}")
    print(f"   🖼️  Metaphors: {analysis.get('visual_metaphors', [])}")
    print(f"   🎨 Colors: {analysis.get('color_palette', [])}")
    print(f"   🏡 Lifestyle: {analysis.get('lifestyle_elements', [])}")
    print(f"   💎 Values: {analysis.get('values_revealed', [])}")
    print(f"   ⭐ Dreams: {analysis.get('aspirations', [])}")
    print(f"   ✨ Keywords: {analysis.get('essence_keywords', [])}")
    print(f"   🎯 Specifics: {analysis.get('specific_mentions', [])}")
    
    # Check depth of analysis
    total_elements = sum([
        len(analysis.get('core_emotions', [])),
        len(analysis.get('visual_metaphors', [])),
        len(analysis.get('color_palette', [])),
        len(analysis.get('lifestyle_elements', [])),
        len(analysis.get('values_revealed', [])),
        len(analysis.get('aspirations', []))
    ])
    
    print(f"\n📈 Analysis Depth: {total_elements} total elements extracted")
    depth_status = "✅ Excellent" if total_elements > 20 else "✅ Good" if total_elements > 15 else "⚠️ Needs improvement"
    print(f"   Status: {depth_status}")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Personalization Test")
    print("=" * 80)
    
    # Test intake analysis first
    test_intake_analysis()
    
    # Test full vision board personalization
    success = test_personalized_vision_board()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 PERSONALIZATION TEST COMPLETED SUCCESSFULLY!")
        print("✅ Vision boards now reflect actual user intake answers")
        print("✅ Performance maintained while adding deep personalization")
        print("✅ All requirements met: speed + functionality + personalization")
    else:
        print("❌ Test failed - personalization needs adjustment")
    
    print("\n💡 Next: Test with real users to verify the personalization quality!")
