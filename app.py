import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Configure logging FIRST - Use INFO for cloud deployment visibility
from core.logging_config import setup_logging
from core.cloud_logging import cloud_logger

# Determine log level based on environment
import sys
is_cloud_deployment = os.getenv('RENDER') or os.getenv('PYTHON_ENV') == 'production'
log_level = "INFO" if is_cloud_deployment else "WARNING"
setup_logging(log_level)

from core.database import DatabaseManager
from core.memory import MemoryManager
from core.smart_agent import SmartAgent
from core.user_profile import UserProfileManager
from core.notification_system import NotificationSystem
from core.voice_handler import VoiceHandler
from core.auth import AuthenticationManager
from core.session_manager import SessionManager
from ui.chat_interface import ChatInterface
from ui.sidebar import SidebarInterface
from ui.analytics import AnalyticsDashboard
from ui.auth_interface import AuthInterface

# Load environment variables
load_dotenv()

# Cloud deployment directory setup
def setup_cloud_directories():
    """Setup required directories for cloud deployment"""
    directories = [
        'user_profiles',
        'vector_stores',
        'logs',
        'temp',
        'data',
        'database'
    ]
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            else:
                print(f"📁 Directory already exists: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")

def log_startup_banner():
    """Display startup banner and environment info for visibility in cloud logs"""
    cloud_logger.log_startup_info()

def log_component_status(component_name: str, status: str, details: str = "", error: Exception = None):
    """Log component initialization status with clear formatting"""
    cloud_logger.log_component_status(component_name, status, details, error)

def initialize_cloud_databases():
    """Initialize databases and create default files for cloud deployment"""
    try:
        # Create default user profile if it doesn't exist
        default_profile_path = os.path.join('user_profiles', 'default_user_profile.json')
        if not os.path.exists(default_profile_path):
            default_profile = {
                "user_id": "default_user",
                "preferences": {
                    "notification_time": "09:00",
                    "timezone": "UTC",
                    "language": "en"
                },
                "habits": [],
                "goals": [],
                "conversation_topics": [],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(default_profile_path, 'w', encoding='utf-8') as f:
                json.dump(default_profile, f, indent=2)
            print("✅ Created default user profile")
        
        # Initialize vector store directory with placeholder
        vector_store_path = os.path.join('vector_stores', '.gitkeep')
        if not os.path.exists(vector_store_path):
            with open(vector_store_path, 'w') as f:
                f.write("# Vector stores will be created here\n")
            print("✅ Created vector store placeholder")
        
        # Create logs directory with placeholder
        logs_path = os.path.join('logs', 'app.log')
        if not os.path.exists(logs_path):
            with open(logs_path, 'w') as f:
                f.write(f"Application started at {datetime.now().isoformat()}\n")
            print("✅ Created log file")
            
    except Exception as e:
        print(f"❌ Error initializing cloud databases: {e}")

def ensure_database_file():
    """Ensure the SQLite database file exists"""
    try:
        db_path = 'noww_club.db'
        if not os.path.exists(db_path):
            # Create empty database file
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.close()
            print("✅ Created SQLite database file")
        else:
            print("📊 Database file already exists")
    except Exception as e:
        print(f"❌ Error creating database file: {e}")

# Page configuration
st.set_page_config(
    page_title="Noww Club AI",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'current_chat_session' not in st.session_state:
        st.session_state.current_chat_session = None
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'show_auth' not in st.session_state:
        st.session_state.show_auth = True
    if 'current_flow' not in st.session_state:
        st.session_state.current_flow = None
    if 'pending_confirmation' not in st.session_state:
        st.session_state.pending_confirmation = None

# Initialize core components
@st.cache_resource
def initialize_components():
    """Initialize all components with detailed logging for cloud visibility"""
    try:
        print("\n🔧 COMPONENT INITIALIZATION")
        print("-" * 60)
        
        # Setup cloud environment first
        print("🚀 Setting up cloud environment...")
        setup_cloud_directories()
        initialize_cloud_databases()
        ensure_database_file()
        
        # Database Manager
        try:
            db_manager = DatabaseManager()
            log_component_status("Database Manager", "SUCCESS", "SQLite database ready")
        except Exception as e:
            log_component_status("Database Manager", "ERROR", str(e))
            raise
        
        # Memory Manager (with Pinecone fallback)
        try:
            memory_manager = MemoryManager(db_manager)
            cloud_logger.log_memory_status(
                memory_manager.using_pinecone,
                "Ready for conversations and vision boards"
            )
        except Exception as e:
            log_component_status("Memory Manager", "ERROR", str(e), e)
            raise
        
        # Smart Agent
        try:
            smart_agent = SmartAgent(db_manager, memory_manager)
            log_component_status("Smart Agent", "SUCCESS", "GPT-4o ready")
        except Exception as e:
            log_component_status("Smart Agent", "ERROR", str(e))
            raise
        
        # Profile Manager
        try:
            profile_manager = UserProfileManager(db_manager)
            log_component_status("Profile Manager", "SUCCESS", "User profiles ready")
        except Exception as e:
            log_component_status("Profile Manager", "ERROR", str(e))
            raise
        
        # Notification System
        try:
            notification_system = NotificationSystem(db_manager)
            log_component_status("Notification System", "SUCCESS", "Notifications ready")
        except Exception as e:
            log_component_status("Notification System", "WARNING", f"Non-critical: {e}")
            notification_system = None
        
        # Voice Handler
        try:
            voice_handler = VoiceHandler()
            log_component_status("Voice Handler", "SUCCESS", "Voice features ready")
        except Exception as e:
            log_component_status("Voice Handler", "WARNING", f"Non-critical: {e}")
            voice_handler = None
        
        # Authentication Manager
        try:
            auth_manager = AuthenticationManager(db_manager)
            log_component_status("Auth Manager", "SUCCESS", "Authentication ready")
        except Exception as e:
            log_component_status("Auth Manager", "ERROR", str(e))
            raise
        
        # Session Manager
        try:
            session_manager = SessionManager(auth_manager)
            log_component_status("Session Manager", "SUCCESS", "Session handling ready")
        except Exception as e:
            log_component_status("Session Manager", "ERROR", str(e))
            raise
        
        print("-" * 60)
        print("✅ ALL CORE COMPONENTS INITIALIZED SUCCESSFULLY")
        cloud_logger.log_app_ready(8)  # 8 components total
        
        return {
            'db_manager': db_manager,
            'memory_manager': memory_manager,
            'smart_agent': smart_agent,
            'profile_manager': profile_manager,
            'notification_system': notification_system,
            'voice_handler': voice_handler,
            'auth_manager': auth_manager,
            'session_manager': session_manager
        }
    except Exception as e:
        print("-" * 60)
        print(f"❌ CRITICAL ERROR IN COMPONENT INITIALIZATION: {e}")
        print("🛑 Application cannot start without core components")
        print("=" * 60)
        st.error(f"Failed to initialize components: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_environment():
    """Check if all required environment variables are set with enhanced logging"""
    required_vars = ['OPENAI_API_KEY']
    optional_vars = {
        'GOOGLE_CLIENT_ID': 'Google OAuth authentication',
        'GOOGLE_CLIENT_SECRET': 'Google OAuth authentication',
        'GOOGLE_REDIRECT_URI': 'Google OAuth authentication',
        'SUPABASE_URL': 'Supabase authentication',
        'SUPABASE_KEY': 'Supabase authentication',
        'JWT_SECRET_KEY': 'JWT token encryption (auto-generated if not provided)',
        'PINECONE_API_KEY': 'Enhanced vector memory storage'
    }
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var, description in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"{var} ({description})")
    
    # Use cloud logger for environment check
    cloud_logger.log_environment_check(missing_required, missing_optional)
    
    if missing_required:
        st.error(f"Missing required environment variables: {', '.join(missing_required)}")
        st.info("Please set these in your environment or .env file")
        return False
    
    if missing_optional:
        st.info(f"Optional environment variables not set: {len(missing_optional)} items")
        st.info("Some advanced features may not be available")
    
    return True

def main():
    try:
        # For cloud deployment, run health check first
        if os.getenv('RENDER'):
            print("\n🏥 Running deployment health check...")
            try:
                from deployment_health_check import log_deployment_status
                log_deployment_status()
            except Exception as e:
                print(f"⚠️  Health check failed: {e}")
        
        # Display startup banner for cloud log visibility
        log_startup_banner()
        
        # Initialize session state
        initialize_session_state()
        
        # Debug: Check for OAuth callback
        query_params = st.query_params
        if query_params:
            print(f"🔗 Query params detected: {dict(query_params)}")
        
        # Check environment variables first
        print("\n🔍 ENVIRONMENT CHECK")
        print("-" * 60)
        if not check_environment():
            print("❌ Environment check failed - stopping application")
            st.stop()
        else:
            print("✅ Environment variables validated")
        
        # Initialize components
        components = initialize_components()
        
        if not components:
            st.error("Failed to initialize application components")
            st.stop()
        
        # Initialize session manager
        session_manager = components['session_manager']
        session_manager.initialize_session()
        
        # Initialize auth interface
        auth_interface = AuthInterface(components['auth_manager'], session_manager)
        
        # Check if user is authenticated
        if not session_manager.is_authenticated():
            # Show authentication interface
            auth_interface.render_auth_interface()
            return
        
        # User is authenticated - show main app
        render_main_app(components, auth_interface)
        
    except Exception as e:
        st.error(f"An error occurred during application startup: {e}")
        st.info("Please check your environment variables and try refreshing the page.")
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

def render_main_app(components, auth_interface):
    """Render the main application interface"""
    # Create main layout
    st.markdown("""
    <div style="text-align: center; padding: 25px 0; background: linear-gradient(135deg, #E8D8F5 0%, #F3E8FF 100%); border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(147, 51, 234, 0.15);">
        <h1 style="color: #6B46C1; font-size: 2.2rem; font-weight: 600; margin-bottom: 8px; text-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">
            🤝 Noww Club AI
        </h1>
        <p style="color: #7C3AED; font-size: 1rem; font-weight: 400; margin: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">
            Your Digital Bestie
        </p>
        <div style="margin-top: 18px; display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
            <span style="background-color: rgba(147, 51, 234, 0.15); border: none; color: #6B46C1; padding: 8px 16px; text-align: center; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; border-radius: 20px; backdrop-filter: blur(10px); font-weight: 500;">💭 Reflect/Talk</span>
            <span style="background-color: rgba(147, 51, 234, 0.15); border: none; color: #6B46C1; padding: 8px 16px; text-align: center; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; border-radius: 20px; backdrop-filter: blur(10px); font-weight: 500;">💎 Habit/Reminder</span>
            <span style="background-color: rgba(147, 51, 234, 0.15); border: none; color: #6B46C1; padding: 8px 16px; text-align: center; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; border-radius: 20px; backdrop-filter: blur(10px); font-weight: 500;">🧘‍♀️ Mindful Rituals</span>
            <span style="background-color: rgba(147, 51, 234, 0.15); border: none; color: #6B46C1; padding: 8px 16px; text-align: center; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; border-radius: 20px; backdrop-filter: blur(10px); font-weight: 500;">🎨 Vision Board</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Render user profile and chat session management in sidebar
    auth_interface.render_user_profile_dropdown()
    auth_interface.render_chat_session_sidebar()
    
    # Get current user profile ID for compatibility
    user_profile_id = components['session_manager'].get_current_user_profile_id()
    
    # Chat interface with session management
    chat_interface = ChatInterface(
        components['smart_agent'],
        components['memory_manager'],
        user_profile_id,
        components['voice_handler'],
        components['session_manager']
    )
    chat_interface.render()

    # Sidebar interface
    sidebar = SidebarInterface(
        components['profile_manager'],
        components['notification_system'],
        user_profile_id,
        chat_interface._handle_lifestyle_action  # Pass action handler
    )
    sidebar.render()
    
    # Handle proactive messages
    if st.session_state.get('show_proactive_message'):
        handle_proactive_messages(components)

def handle_proactive_messages(components):
    """Handle proactive messaging system"""
    try:
        # Get current user ID
        user_id = components['session_manager'].get_current_user_profile_id()
        if not user_id:
            return
        
        # Check for pending flows or suggestions
        pending_flows = components['db_manager'].get_pending_flows(user_id)
        
        if pending_flows:
            with st.container():
                st.markdown(
                    """
                    <div style="border: 2px solid #4CAF50; padding: 15px; margin: 15px 0; border-radius: 12px; background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%); box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);">
                        <p style="margin: 0 0 10px 0;"><strong>🔔 Proactive Message:</strong></p>
                        <p style="margin: 0;">I noticed you have an incomplete flow. Would you like to continue where we left off?</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Continue Flow", type="primary"):
                        st.session_state.resume_flow = True
                        st.rerun()
                with col2:
                    if st.button("🔄 Start Fresh"):
                        components['db_manager'].clear_pending_flows(user_id)
                        st.session_state.show_proactive_message = False
                        st.rerun()
    except Exception as e:
        print(f"Error in proactive messages: {e}")

# Cloud deployment health check
def health_check():
    """Simple health check for cloud deployment"""
    try:
        # Check if directories exist
        required_dirs = ['user_profiles', 'vector_stores', 'logs']
        for directory in required_dirs:
            if not os.path.exists(directory):
                return False
        
        # Check if database file exists
        if not os.path.exists('noww_club.db'):
            return False
        
        # Check environment variables
        if not os.getenv('OPENAI_API_KEY'):
            return False
        
        return True
    except:
        return False

if __name__ == "__main__":
    # Add health check endpoint for cloud monitoring
    if st.sidebar.button("🏥 Health Check"):
        if health_check():
            st.sidebar.success("✅ All systems operational")
        else:
            st.sidebar.error("❌ System check failed")
    
    main()
