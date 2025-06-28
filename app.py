import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from core.database import DatabaseManager
from core.memory import MemoryManager
from core.smart_agent import SmartAgent
from core.user_profile import UserProfileManager
from core.notification_system import NotificationSystem
from core.voice_handler import VoiceHandler
from ui.chat_interface import ChatInterface
from ui.sidebar import SidebarInterface
from ui.analytics import AnalyticsDashboard
from utils.notifications import NotificationManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Noww Club AI",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.user_id = "default_user"  # In production, this would be from authentication
    st.session_state.messages = []
    st.session_state.current_flow = None
    st.session_state.pending_confirmation = None

# Initialize core components
@st.cache_resource
def initialize_components():
    db_manager = DatabaseManager()
    memory_manager = MemoryManager(db_manager)
    smart_agent = SmartAgent(db_manager, memory_manager)
    profile_manager = UserProfileManager(db_manager)
    notification_manager = NotificationManager(db_manager)
    notification_system = NotificationSystem(db_manager)
    voice_handler = VoiceHandler()
    
    return {
        'db_manager': db_manager,
        'memory_manager': memory_manager,
        'smart_agent': smart_agent,
        'profile_manager': profile_manager,
        'notification_manager': notification_manager,
        'notification_system': notification_system,
        'voice_handler': voice_handler
    }

def main():
    try:
        # Initialize components
        components = initialize_components()
        
        # Create main layout
        st.markdown("""
        <div style="text-align: center; padding: 20px 0; background-color: #7B68EE; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; font-size: 2.5rem; font-weight: 700; margin-bottom: 5px;">
                🤝 Noww Club AI
            </h1>
            <p style="color: #E6E6FA; font-size: 1.1rem; font-weight: 500; margin: 0;">
                Your Digital Bestie
            </p>
            <div style="margin-top: 15px; display: flex; justify-content: center; gap: 10px;">
                <button style="background-color: rgba(255, 255, 255, 0.2); border: none; color: white; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; border-radius: 16px; cursor: pointer;">🧠 Memory</button>
                <button style="background-color: rgba(255, 255, 255, 0.2); border: none; color: white; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; border-radius: 16px; cursor: pointer;">🔍 Search</button>
                <button style="background-color: rgba(255, 255, 255, 0.2); border: none; color: white; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; border-radius: 16px; cursor: pointer;">🚀 Proactive</button>
                <button style="background-color: rgba(255, 255, 255, 0.2); border: none; color: white; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; border-radius: 16px; cursor: pointer;">🌟 Adaptive</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat interface
        chat_interface = ChatInterface(
            components['smart_agent'],
            components['memory_manager'],
            st.session_state.user_id,
            components['voice_handler']
        )
        chat_interface.render()
    
        # Sidebar interface
        sidebar = SidebarInterface(
            components['profile_manager'],
            components['notification_manager'],
            st.session_state.user_id
        )
        sidebar.render()
        
        # Handle proactive messages
        if st.session_state.get('show_proactive_message'):
            handle_proactive_messages(components)

    except Exception as e:
        st.error(f"An error occurred during application startup: {e}")
        st.info("Please ensure your environment variables (like OPENAI_API_KEY) are set correctly and try again.")

def handle_proactive_messages(components):
    """Handle proactive messaging system"""
    notification_manager = components['notification_manager']
    
    # Check for pending flows or suggestions
    pending_flows = components['db_manager'].get_pending_flows(st.session_state.user_id)
    
    if pending_flows:
        with st.container():
            st.markdown(
                """
                <div style="border: 2px dotted #4CAF50; padding: 10px; margin: 10px 0; border-radius: 10px; background-color: #f0f8f0;">
                    <p><strong>🔔 Proactive Message:</strong></p>
                    <p>I noticed you have an incomplete flow. Would you like to continue where we left off?</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Continue Flow"):
                    st.session_state.resume_flow = True
                    st.rerun()
            with col2:
                if st.button("Start Fresh"):
                    components['db_manager'].clear_pending_flows(st.session_state.user_id)
                    st.session_state.show_proactive_message = False
                    st.rerun()

if __name__ == "__main__":
    main()
