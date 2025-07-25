#!/usr/bin/env python3
"""
Test script for magazine-style vision board generation with actual user responses
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from core.vision_board_generator import VisionBoardGenerator
from core.database import DatabaseManager
from core.memory import ModernConversationMemory
from core.session_manager import SessionManager
from core.auth import AuthenticationManager
from utils.prompt_loader import PromptLoader

def test_magazine_vision_board():
    """Test magazine-style vision board generation with actual user responses"""
    print("🎨 Testing Magazine-Style Vision Board Generation...")
    print("=" * 60)
    
    try:
        # Initialize components
        print("📋 Initializing components...")
        db_manager = DatabaseManager()
        
        # Initialize memory with dummy LLM for testing
        class DummyLLM:
            def __call__(self, prompt):
                return "test response"
        
        memory = ModernConversationMemory(llm=DummyLLM())
        session_manager = SessionManager()
        auth_manager = AuthenticationManager()
        prompt_loader = PromptLoader()
        
        vision_board_gen = VisionBoardGenerator(
            db_manager=db_manager,
            memory=memory,
            session_manager=session_manager,
            auth_manager=auth_manager,
            prompt_loader=prompt_loader
        )
        
        # Create test user with actual responses
        test_user_id = "test_magazine_user"
        print(f"👤 Setting up test user: {test_user_id}")
        
        # Simulate actual vision board intake responses
        actual_responses = [
            "unshakable clarity",
            "mind-bending AI",
            "emotional intelligence",
            "revolutionary breakthrough",
            "unstoppable innovation",
            "global recognition",
            "premium lifestyle",
            "authentic success"
        ]
        
        # Store intake data directly in the database
        print("💾 Storing actual user intake responses...")
        
        # Create intake data structure
        intake_data = {
            "responses": actual_responses,
            "completed_at": datetime.now().isoformat(),
            "persona_extracted": True
        }
        
        # Store in database
        db_manager.execute_query(
            """INSERT OR REPLACE INTO vision_board_intake 
               (user_id, intake_data, completed_at) 
               VALUES (?, ?, ?)""",
            (test_user_id, json.dumps(intake_data), datetime.now().isoformat())
        )
        
        print("✅ Intake data stored successfully")
        
        # Test persona extraction
        print("\n🧠 Testing persona extraction with actual responses...")
        persona = vision_board_gen._extract_user_persona(actual_responses)
        print(f"✅ Persona extracted: {type(persona)}")
        print(f"📊 Persona preview: {str(persona)[:100]}...")
        
        # Test template selection
        print("\n🎯 Testing template selection...")
        template_num = vision_board_gen._select_template_for_user(test_user_id)
        print(f"✅ Selected template: {template_num}")
        
        # Test the new magazine-style prompt generation
        print("\n📝 Testing magazine-style prompt generation...")
        
        # Get intake data for vision board
        intake_data_from_db = vision_board_gen.intake_manager.get_intake_data_for_vision_board(test_user_id)
        print(f"✅ Retrieved intake data: {len(intake_data_from_db.get('responses', []))} responses")
        
        # Generate the magazine-style prompt
        prompt = vision_board_gen.customize_prompt_with_intake_data(
            template_num, persona, actual_responses
        )
        
        print(f"✅ Magazine prompt generated: {len(prompt)} characters")
        print("\n📋 Prompt Preview (first 500 chars):")
        print("-" * 50)
        print(prompt[:500] + "...")
        print("-" * 50)
        
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
            "revolutionary breakthrough"
        ]
        
        for element in magazine_elements:
            if element.lower() in prompt.lower():
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
        
        # Test actual vision board generation
        print("\n🖼️ Testing actual vision board generation...")
        print("⚠️  Note: This will use OpenAI DALL-E API and may take a moment...")
        
        # Generate the vision board
        result = vision_board_gen.generate_vision_board(test_user_id)
        
        if result and result.get('success'):
            print("✅ Vision board generated successfully!")
            print(f"🖼️  Image URL: {result.get('image_url', 'N/A')}")
            print(f"📄 Template: {result.get('template_name', 'N/A')}")
            
            # Check if file was saved
            if 'temp' in str(result.get('image_url', '')):
                print(f"💾 Vision board saved locally")
        else:
            print("❌ Vision board generation failed")
            print(f"🔍 Result: {result}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_magazine_vision_board()
