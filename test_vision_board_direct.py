"""
Direct test of vision board functionality without Streamlit
"""
import sys
import os
sys.path.append('.')

# Disable Python bytecode generation to avoid cache issues
sys.dont_write_bytecode = True

# Mock streamlit session state for testing
class MockSessionState:
    def __init__(self):
        self.authenticated = False
        self.user_id = None
        self.user_info = None
        self.current_chat_session = None
        self.chat_sessions = []
        self.messages = []
        self.show_auth = True

# Replace streamlit's session_state with our mock
import streamlit as st
if not hasattr(st, 'session_state'):
    st.session_state = MockSessionState()

from dotenv import load_dotenv
from core.database import DatabaseManager
from core.memory import MemoryManager
from core.smart_agent import SmartAgent
from core.vision_board_generator import VisionBoardGenerator
from core.session_manager import SessionManager
from core.auth import AuthenticationManager
from utils.prompt_loader import PromptLoader

# Load environment variables
load_dotenv()

def test_vision_board_generation():
    """Test vision board generation directly"""
    print("🧪 Testing Vision Board Generation...")
    
    try:
        # Initialize components
        print("📋 Initializing components...")
        
        # Database
        db_manager = DatabaseManager()
        print("✅ Database initialized")
        
        # Memory system  
        memory_manager = MemoryManager()
        print("✅ Memory system initialized")
        
        # Prompt loader
        prompt_loader = PromptLoader()
        print("✅ Prompt loader initialized")
        
        # Auth manager
        auth_manager = AuthenticationManager(db_manager)
        print("✅ Auth manager initialized")
        
        # Session manager
        session_manager = SessionManager(auth_manager)
        print("✅ Session manager initialized")
        
        # Smart agent
        smart_agent = SmartAgent(
            db_manager=db_manager,
            memory_manager=memory_manager
        )
        print("✅ Smart agent initialized")
        
        # Vision board generator
        vision_generator = VisionBoardGenerator(
            db_manager=db_manager,
            memory_manager=memory_manager
        )
        print("✅ Vision board generator initialized")
        
        print("\n🎨 Testing Vision Board Creation...")
        
        # Create a test user context
        test_user_id = "test_user_vision_board"
        test_session_id = "test_session_vision_board"
        
        # Test persona extraction
        print("👤 Testing persona extraction...")
        
        persona = vision_generator.extract_user_persona(test_user_id)
        print(f"✅ Persona extracted: {type(persona)} - {str(persona)[:100]}...")
        
        # Test template selection
        print("🎯 Testing template selection...")
        template_num = vision_generator.analyze_user_for_template(test_user_id)
        print(f"✅ Selected template: {template_num}")
        
        # Test vision board generation
        print("🖼️ Testing vision board generation...")
        
        # Mock user message
        user_message = "Create a vision board for me"
        conversation_history = [
            "I want to become a successful entrepreneur",
            "I love fitness and working out every morning", 
            "My goal is to build a tech startup",
            "I'm passionate about personal development"
        ]
        
        try:
            image_url, template_name = vision_generator.generate_vision_board(user_id=test_user_id)
            
            if image_url and template_name:
                print("🎉 SUCCESS! Vision board generated successfully!")
                print(f"📁 Image URL: {image_url}")
                print(f"🎨 Template used: {template_name}")
                
                # Test download
                print("💾 Testing image download...")
                import requests
                response = requests.get(image_url)
                if response.status_code == 200:
                    print("✅ Image download successful!")
                    
                    # Save to temp folder
                    temp_path = f"temp/test_vision_board_{test_user_id}.png"
                    with open(temp_path, 'wb') as f:
                        f.write(response.content)
                    print(f"💾 Saved test image to: {temp_path}")
                else:
                    print(f"❌ Image download failed: {response.status_code}")
                
                return True
            else:
                print(f"❌ Vision board generation failed: image_url={image_url}, template_name={template_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error during vision board generation: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error during component initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_agent_integration():
    """Test smart agent vision board integration"""
    print("\n🤖 Testing Smart Agent Integration...")
    
    try:
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager()
        prompt_loader = PromptLoader()
        auth_manager = AuthenticationManager(db_manager)
        session_manager = SessionManager(auth_manager)
        
        smart_agent = SmartAgent(
            db_manager=db_manager,
            memory_manager=memory_manager
        )
        
        # Test vision board intent detection
        test_messages = [
            "Create a vision board for me",
            "I want to visualize my goals",
            "Show me my future", 
            "Generate my dream board",
            "Help me visualize my dreams",
            "What's the weather like?",  # Non-vision board
            "I want a vision board"
        ]
        
        print("🔍 Testing intent detection...")
        for message in test_messages:
            is_vision_board = smart_agent.check_for_vision_board_intent(message)
            status = "✅" if is_vision_board else "❌"
            expected = "should detect" if any(word in message.lower() for word in ['vision', 'visualize', 'dream']) else "should NOT detect"
            print(f"{status} '{message}' - {expected}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing smart agent integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Vision Board Tests...")
    print("=" * 60)
    
    # Test 1: Direct vision board generation
    test1_result = test_vision_board_generation()
    
    # Test 2: Smart agent integration
    test2_result = test_smart_agent_integration()
    
    print("\n" + "=" * 60)
    print("🏁 Test Results:")
    print(f"✅ Vision Board Generation: {'PASSED' if test1_result else 'FAILED'}")
    print(f"✅ Smart Agent Integration: {'PASSED' if test2_result else 'FAILED'}")
    
    if test1_result and test2_result:
        print("🎉 All tests passed! Vision board functionality is ready!")
    else:
        print("❌ Some tests failed. Please check the errors above.")
