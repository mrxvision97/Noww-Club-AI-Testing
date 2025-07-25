import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time
import re
import base64
import requests
import traceback
from io import BytesIO
from PIL import Image
# Smart agent handles all processing
from core.memory import MemoryManager

class ChatInterface:
    def __init__(self, smart_agent, memory_manager: MemoryManager, user_id: str, voice_handler=None, session_manager=None):
        self.smart_agent = smart_agent
        self.memory_manager = memory_manager
        self.user_id = user_id
        self.voice_handler = voice_handler
        self.session_manager = session_manager
    
    def _get_user_name(self):
        """Get user's name from profile or session, with fallback"""
        try:
            # Try to get from user profile
            if hasattr(self.smart_agent, 'user_profile_manager'):
                profile = self.smart_agent.user_profile_manager.get_user_profile(self.user_id)
                if profile and profile.get('name'):
                    return profile['name']
            
            # Try to get from session if available
            if self.session_manager and hasattr(self.session_manager, 'get_user_name'):
                name = self.session_manager.get_user_name()
                if name:
                    return name
            
            # Fallback to a friendly generic greeting
            return None
        except:
            return None
    
    def _get_welcome_message(self):
        """Generate personalized welcome message"""
        user_name = self._get_user_name()
        if user_name:
            return f"✨ Welcome {user_name}! This is a space where you can:"
        else:
            return "✨ Welcome! This is a space where you can:"
    
    def _get_ist_time(self, timestamp=None):
        """Convert timestamp to Local Time (corrected)"""
        if timestamp is None:
            # Get current local time
            return datetime.now()
        
        if isinstance(timestamp, str):
            # Parse ISO format timestamp
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                # If parsing fails, return current time
                return datetime.now()
        
        # If timestamp has timezone info, convert to local time
        if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
            return timestamp.astimezone()
        else:
            # If no timezone info, assume it's UTC and convert to local
            from datetime import timezone
            timestamp = timestamp.replace(tzinfo=timezone.utc)
            return timestamp.astimezone()
    
    def render(self):
        """Render the chat interface"""
        # Initialize messages consistently - always use 'messages' key
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Get messages from session state
        messages = st.session_state.messages
        
        # Display chat history
        self._display_chat_history(messages)
        
        # Show lifestyle concierge tabs only when no messages (welcome state)
        if not messages:
            self._render_lifestyle_concierge_tabs()
        
        # Chat input (this appears at the bottom of the screen)
        self._render_chat_input()
        
        # Handle flow resumption
        if st.session_state.get("resume_flow"):
            self._handle_flow_resumption()
    
    def _display_chat_history(self, messages=None):
        """Display the conversation history with styled bubbles"""
        
        # Use provided messages or get from session state
        if messages is None:
            messages = st.session_state.get('messages', [])
        
        # Add custom CSS for chat bubbles with enhanced modern styling
        st.markdown("""
        <style>
        /* Import Inter font for consistency */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 12px;
            height: calc(100vh - 300px);
            min-height: 400px;
            overflow-y: auto;
            padding: 20px;
            border: none;
            border-radius: 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
            font-family: 'Inter', sans-serif;
        }
        
        .user-message {
            align-self: flex-end;
            background: linear-gradient(135deg, #E8D8F5 0%, #DDD6FE 100%);
            color: #6B46C1;
            padding: 14px 18px;
            border-radius: 18px 18px 6px 18px;
            max-width: 80%;
            margin-left: auto;
            word-wrap: break-word;
            box-shadow: 0 2px 8px rgba(147, 51, 234, 0.15), 0 1px 3px rgba(0,0,0,0.1);
            animation: slideInRight 0.3s ease-out;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            line-height: 1.4;
        }
        
        .ai-message {
            align-self: flex-start;
            background: #ffffff;
            color: #2d3748;
            padding: 16px 20px;
            border-radius: 18px 18px 18px 6px;
            max-width: 85%;
            margin-right: auto;
            word-wrap: break-word;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            animation: slideInLeft 0.3s ease-out;
            line-height: 1.6;
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
        }
        
        .ai-message b {
            color: #7C3AED;
            font-size: 1em;
            font-weight: 600;
            margin-bottom: 8px;
            display: block;
        }
        
        .ai-message ul, .ai-message ol {
            margin: 10px 0;
            padding-left: 20px;
        }
        
        .ai-message li {
            margin: 4px 0;
            line-height: 1.5;
        }
        
        .ai-message h3, .ai-message h4 {
            color: #2d3748;
            margin: 12px 0 6px 0;
            font-weight: 600;
        }
        
        .proactive-message {
            align-self: flex-start;
            background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
            color: #065f46;
            padding: 14px 18px;
            border: 1px solid #34d399;
            border-radius: 18px 18px 18px 6px;
            max-width: 80%;
            margin-right: auto;
            word-wrap: break-word;
            animation: bounceIn 0.5s ease-out;
            box-shadow: 0 1px 3px rgba(52, 211, 153, 0.15);
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }
        
        .typing-indicator {
            animation: blink 1s infinite;
            color: #7C3AED;
            font-weight: 600;
            font-size: 1.1em;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        @keyframes slideInRight {
            from { transform: translateX(20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideInLeft {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.02); }
            70% { transform: scale(0.98); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .timestamp {
            font-size: 0.8rem;
            color: #94a3b8;
            text-align: center;
            margin: 6px 0;
            font-style: italic;
            font-family: 'Inter', sans-serif;
            font-weight: 400;
        }
        
        /* Scrollbar styling */
        .chat-container::-webkit-scrollbar {
            width: 4px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        /* Mobile responsiveness for chat */
        @media (max-width: 768px) {
            .chat-container {
                padding: 16px;
                height: calc(100vh - 250px);
                min-height: 350px;
            }
            
            .user-message, .ai-message, .proactive-message {
                font-size: 0.9rem;
                padding: 12px 16px;
                max-width: 90%;
            }
            
            .ai-message b {
                font-size: 0.95em;
            }
        }
        
        /* Vision board styling within chat */
        .vision-board-container {
            align-self: flex-start;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 16px;
            margin: 8px 0;
            max-width: 90%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .vision-board-image {
            width: 100%;
            border-radius: 12px;
            margin-bottom: 12px;
        }
        
        .vision-board-title {
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }
        
        .vision-board-download {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            text-decoration: none;
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            font-weight: 500;
            display: inline-block;
            margin-top: 8px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create chat container
        if messages:
            chat_html = '<div class="chat-container" id="chat-container">'
            
            for i, message in enumerate(messages):
                # Add timestamp for first message or messages more than 5 minutes apart
                if i == 0 or self._should_show_timestamp(i, messages):
                    timestamp = message.get("timestamp", datetime.now())
                    # Convert to IST and display
                    ist_timestamp = self._get_ist_time(timestamp)
                    chat_html += f'<div class="timestamp">{ist_timestamp.strftime("%I:%M %p IST")}</div>'
                
                role = message["role"]
                content = message["content"]
                message_type = message.get("type", "normal")
                
                if role == "user":
                    chat_html += f'<div class="user-message">{content}</div>'
                else:
                    if message_type == "proactive":
                        chat_html += f'<div class="proactive-message">🔔 {content}</div>'
                    elif message_type == "vision_board":
                        # Display vision board inline with chat
                        image_url = message.get("image_url")
                        template_name = message.get("template_name", "Custom")
                        if image_url:
                            chat_html += f'''
                            <div class="vision-board-container">
                                <div class="vision-board-title">🎨 Your Personalized Vision Board - {template_name}</div>
                                <img src="{image_url}" alt="Vision Board" class="vision-board-image">
                                <a href="{image_url}" download="vision_board.jpg" class="vision-board-download">📥 Download Your Vision Board</a>
                            </div>
                            '''
                        else:
                            chat_html += f'<div class="ai-message"><b>Noww Club AI</b><br>🎨 Your Vision Board - {template_name}</div>'
                    else:
                        # Display AI message with proper HTML formatting
                        chat_html += f'<div class="ai-message"><b>Noww Club AI</b><br>{content}</div>'
            
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
            
            # Enhanced auto-scroll with improved reliability
            st.markdown("""
            <script>
            (function() {
                // More robust scroll function
                function forceScrollToBottom() {
                    const chatContainer = document.getElementById('chat-container');
                    if (!chatContainer) return false;
                    
                    // Multiple scroll strategies for maximum compatibility
                    try {
                        // Strategy 1: Direct scrollTop assignment
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                        
                        // Strategy 2: scrollTo with instant behavior for reliability
                        chatContainer.scrollTo({
                            top: chatContainer.scrollHeight,
                            behavior: 'instant'
                        });
                        
                        // Strategy 3: scrollIntoView on last element
                        const messages = chatContainer.children;
                        if (messages.length > 0) {
                            const lastMessage = messages[messages.length - 1];
                            lastMessage.scrollIntoView({ behavior: 'instant', block: 'end' });
                        }
                        
                        return true;
                    } catch (error) {
                        console.warn('Auto-scroll error:', error);
                        return false;
                    }
                }
                
                // Wait for DOM to be ready
                function waitForContainer(callback, maxAttempts = 50) {
                    let attempts = 0;
                    
                    function check() {
                        const container = document.getElementById('chat-container');
                        if (container || attempts >= maxAttempts) {
                            callback(container);
                        } else {
                            attempts++;
                            setTimeout(check, 100);
                        }
                    }
                    
                    check();
                }
                
                // Initialize auto-scroll when container is ready
                waitForContainer(function(container) {
                    if (!container) return;
                    
                    // Initial scroll attempts
                    forceScrollToBottom();
                    setTimeout(forceScrollToBottom, 100);
                    setTimeout(forceScrollToBottom, 300);
                    setTimeout(forceScrollToBottom, 600);
                    setTimeout(forceScrollToBottom, 1000);
                    
                    // Set up mutation observer for dynamic content
                    const observer = new MutationObserver(function(mutations) {
                        let shouldScroll = false;
                        
                        mutations.forEach(function(mutation) {
                            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                                shouldScroll = true;
                            }
                            if (mutation.type === 'characterData') {
                                shouldScroll = true;
                            }
                        });
                        
                        if (shouldScroll) {
                            // Immediate and delayed scroll
                            forceScrollToBottom();
                            setTimeout(forceScrollToBottom, 50);
                            setTimeout(forceScrollToBottom, 200);
                        }
                    });
                    
                    // Start observing
                    observer.observe(container, { 
                        childList: true, 
                        subtree: true,
                        characterData: true,
                        attributes: true
                    });
                    
                    // Handle window resize
                    window.addEventListener('resize', function() {
                        setTimeout(forceScrollToBottom, 100);
                    });
                    
                    // Periodic scroll check for reliability
                    setInterval(function() {
                        if (container && container.children.length > 0) {
                            const isNearBottom = container.scrollTop >= container.scrollHeight - container.clientHeight - 100;
                            if (isNearBottom) {
                                forceScrollToBottom();
                            }
                        }
                    }, 1000);
                });
                
                // Also try immediate execution
                setTimeout(function() {
                    forceScrollToBottom();
                }, 0);
            })();
            </script>
            """, unsafe_allow_html=True)
        
        else:
            # No welcome message - just show empty state
            pass
    
    def _should_show_timestamp(self, index: int, messages: list) -> bool:
        """Determine if timestamp should be shown"""
        if index == 0:
            return True
        
        current_msg = messages[index]
        prev_msg = messages[index - 1]
        
        current_time = current_msg.get("timestamp")
        prev_time = prev_msg.get("timestamp")
        
        if not current_time or not prev_time:
            return False
        
        # Convert both to IST for comparison
        current_ist = self._get_ist_time(current_time)
        prev_ist = self._get_ist_time(prev_time)
        
        # Show timestamp if more than 5 minutes apart
        time_diff = abs((current_ist - prev_ist).total_seconds())
        return time_diff > 300
    
    def _render_chat_input(self):
        """Render the chat input area using st.chat_input for Enter-to-send."""
        if user_input := st.chat_input("💬 Share your thoughts, dreams, or ask me anything!"):
            self._process_user_message(user_input.strip())
    
    def _render_lifestyle_concierge_tabs(self):
        """Render the lifestyle concierge tabs with icons and descriptions"""
        
        # Create responsive button grid using Streamlit columns
        # For mobile: 2x2 grid, for desktop: 4x1 grid
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
        # Create all buttons with identical parameters to ensure consistency
        with col1:
            if st.button(
                "💭\nReflect/Talk", 
                use_container_width=True,
                help="Share your thoughts, feelings, and reflect on your day with thoughtful guidance",
                key="reflect_talk_btn"
            ):
                self._handle_lifestyle_action("reflect_talk")
        
        with col2:
            if st.button(
                "💎\nHabit/Reminder", 
                use_container_width=True,
                help="Build positive habits and set gentle reminders for your daily routines",
                key="habit_reminder_btn"
            ):
                self._handle_lifestyle_action("habit_reminder")
        
        with col3:
            if st.button(
                "🧘‍♀️\nMindful Rituals", 
                use_container_width=True,
                help="Discover calming practices and mindfulness techniques for intentional living",
                key="mindful_rituals_btn"
            ):
                self._handle_lifestyle_action("mindful_rituals")
        
        with col4:
            if st.button(
                "🎨\nVision Board", 
                use_container_width=True,
                help="Create a personalized vision board to visualize and manifest your dreams",
                key="vision_board_btn"
            ):
                self._handle_lifestyle_action("vision_board")
        
        # Add the bottom text section
        st.markdown("""
        <div class="bottom-text">
            <p>Or just vent! I'm here to listen :)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced styling for modern Gen-Z friendly mobile interface
        st.markdown("""
        <style>
        /* Import modern fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Main app container styling */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 500px;
            margin: 0 auto;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Welcome section */
        .welcome-section {
            text-align: center;
            margin: 20px 0 30px 0;
        }
        
        /* Welcome header styling */
        .welcome-header h2 {
            font-family: 'Inter', sans-serif;
            font-size: 1.4rem;
            font-weight: 600;
            color: #1a202c;
            line-height: 1.4;
            margin: 0;
        }
        
        /* Streamlit button styling - Modern mobile design with enhanced visibility */
        div[data-testid="column"] .stButton > button {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 2px solid #e2e8f0;
            border-radius: 18px;
            color: #1f2937;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            padding: 22px 16px;
            transition: all 0.25s ease;
            height: auto;
            min-height: 90px;
            font-size: 1rem;
            line-height: 1.3;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1), 0 2px 6px rgba(0,0,0,0.06);
            width: 100%;
            margin: 6px 0;
            white-space: pre-line;
            position: relative;
            overflow: hidden;
            opacity: 1;
            visibility: visible;
        }
        
        /* Enhanced hover effects for better visibility */
        div[data-testid="column"] .stButton > button:hover {
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            border-color: #9ca3af;
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15), 0 4px 10px rgba(0,0,0,0.1);
            color: #111827;
            font-weight: 700;
        }
        
        /* Focus and active states */
        div[data-testid="column"] .stButton > button:focus {
            border-color: #4F46E5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15), 0 2px 8px rgba(0,0,0,0.1);
            outline: none;
        }
        
        div[data-testid="column"] .stButton > button:active {
            transform: translateY(-1px);
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        }
        
        /* Bottom text styling */
        .bottom-text {
            text-align: center;
            margin: 25px 0 20px 0;
        }
        
        .bottom-text p {
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            color: #6b7280;
            font-weight: 400;
            margin: 0;
            font-style: italic;
        }
        
        /* Chat input area styling */
        .stChatInput > div {
            border-radius: 25px;
            border: 2px solid #e2e8f0;
            background: #ffffff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
        }
        
        .stChatInput > div:focus-within {
            border-color: #4F46E5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1), 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* Hide Streamlit header and menu */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Improve overall app styling */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .main .block-container {
                max-width: 100%;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            .welcome-header h2 {
                font-size: 1.25rem;
                padding: 0 10px;
            }
            
            div[data-testid="column"] .stButton > button {
                padding: 18px 14px;
                min-height: 80px;
                font-size: 0.85rem;
                border-radius: 14px;
                margin: 3px 0;
            }
            
            .bottom-text p {
                font-size: 0.9rem;
            }
        }
        
        /* Very small mobile screens */
        @media (max-width: 480px) {
            .welcome-header h2 {
                font-size: 1.1rem;
                line-height: 1.3;
                padding: 0 15px;
            }
            
            div[data-testid="column"] .stButton > button {
                padding: 16px 12px;
                min-height: 75px;
                font-size: 0.8rem;
                border-radius: 12px;
            }
            
            .bottom-text p {
                font-size: 0.85rem;
            }
        }
        
        /* Grid spacing improvements */
        div[data-testid="column"] {
            padding: 0 6px;
        }
        
        /* First and last column adjustments */
        div[data-testid="column"]:first-child {
            padding-left: 0;
        }
        
        div[data-testid="column"]:last-child {
            padding-right: 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _handle_lifestyle_action(self, action_type: str):
        """Handle lifestyle concierge actions"""
        action_config = {
            "reflect_talk": {
                "prompt": "I'd like to reflect on my day and check in on how I'm feeling. Can you help me process my thoughts and emotions with thoughtful questions and guidance?",
                "success_message": "Reflection & Talk mode activated! Let's explore your thoughts together.",
                "emoji": "💭"
            },
            "habit_reminder": {
                "prompt": "I want to work on building positive habits and need gentle reminders. Can you help me set up a personalized habit tracking system and provide encouraging nudges?",
                "success_message": "Habit & Reminder mode activated! Let's build positive routines together.",
                "emoji": "🔔"
            },
            "mindful_rituals": {
                "prompt": "I'm interested in incorporating mindful rituals and intentional moments into my daily routine. Can you guide me through calming practices and suggest mindfulness techniques?",
                "success_message": "Mindful Rituals mode activated! Let's embrace calm and intentional moments.",
                "emoji": "🧘‍♀️"
            },
            "vision_board": {
                "prompt": "I want to create a vision board",
                "success_message": "Vision Board mode activated! Let's visualize your dreams together.",
                "emoji": "🎨"
            }
        }
        
        if action_type in action_config:
            config = action_config[action_type]
            
            # Add a visual indication with the specific emoji and message
            st.success(f"{config['emoji']} {config['success_message']}")
            
            # Special handling for vision board
            if action_type == "vision_board":
                self._handle_vision_board_request()
            else:
                # Process the predefined prompt
                self._process_user_message(config['prompt'])
            
            # Brief pause and rerun
            time.sleep(0.5)
            st.rerun()
    
    def _process_user_message(self, message: str):
        """Process user message through the state graph with streaming"""
        # Check if this is a vision board request
        if self._is_vision_board_request(message):
            # Add user message to chat history first
            from datetime import timezone
            utc_time = datetime.now(timezone.utc)
            user_message = {
                "role": "user",
                "content": message,
                "timestamp": utc_time.isoformat()
            }
            
            # Always add to messages in session state
            if "messages" not in st.session_state:
                st.session_state.messages = []
            st.session_state.messages.append(user_message)
            
            # Also save via session manager if available
            if self.session_manager:
                self.session_manager.save_message("user", message)
            
            # Handle vision board request
            self._handle_vision_board_request()
            return
        
        # Add user message to chat history with current UTC time
        from datetime import timezone
        utc_time = datetime.now(timezone.utc)
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": utc_time.isoformat()
        }
        
        # Always add to messages in session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append(user_message)
        
        # Also save via session manager if available
        if self.session_manager:
            self.session_manager.save_message("user", message)
        
        # Create placeholder for streaming response
        response_placeholder = st.empty()
        
        # Show processing indicator
        with st.spinner("🤔 Thinking..."):
            try:
                print(f"Processing message for user {self.user_id}: {message}")
                
                # Process through smart agent
                ai_response = self.smart_agent.process_message(self.user_id, message)
                print(f"✅ AI response generated: {len(ai_response)} characters")
                
                # Format the response for better display
                formatted_response = self._format_ai_response(ai_response)
                
                # Stream the response
                self._stream_response(formatted_response, response_placeholder)
                
                # Add AI response to chat history with current UTC time
                utc_time = datetime.now(timezone.utc)
                ai_message = {
                    "role": "assistant",
                    "content": formatted_response,
                    "timestamp": utc_time.isoformat()
                }
                
                # Always add to messages in session state
                st.session_state.messages.append(ai_message)
                
                # Also save via session manager if available
                if self.session_manager:
                    self.session_manager.save_message("assistant", formatted_response)
                
                # Voice output if enabled
                if (st.session_state.get('voice_output', False) and 
                    self.voice_handler and 
                    self.voice_handler.available):
                    try:
                        # Use original response for voice (without HTML formatting)
                        self.voice_handler.speak_text(ai_response)
                    except Exception as voice_error:
                        print(f"Warning: Voice output failed: {voice_error}")
                
                print(f"✅ Message processing completed for user {self.user_id}")
                
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                import traceback
                traceback.print_exc()
                
                st.error(f"Sorry, I encountered an error: {str(e)}")
                
                # Add fallback response with UTC time
                utc_time = datetime.now(timezone.utc)
                ai_message = {
                    "role": "assistant",
                    "content": "I'm sorry, I encountered an error processing your message. Please try again.",
                    "timestamp": utc_time.isoformat()
                }
                st.session_state.messages.append(ai_message)
        
        # Clear the response placeholder to avoid duplicate content
        response_placeholder.empty()
        
        # Force scroll to new message
        st.markdown("""
        <script>
        setTimeout(function() {
            const chatContainer = document.getElementById('chat-container');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        # Rerun to update the interface
        st.rerun()
    
    def _handle_voice_input(self):
        """Handle voice input from user"""
        if not self.voice_handler or not self.voice_handler.available:
            st.error("Voice input not available - missing dependencies")
            return
        
        try:
            with st.spinner("🎤 Listening... Please speak now"):
                recorded_audio = self.voice_handler.record_audio(duration=5)
                
            if recorded_audio:
                with st.spinner("Processing speech..."):
                    text = self.voice_handler.recognize_speech_from_audio(recorded_audio)
                
                if text:
                    st.success(f"Recognized: {text}")
                    self._process_user_message(text)
                    st.rerun()
                else:
                    st.error("Could not understand the speech. Please try again.")
            else:
                st.error("No audio recorded. Please check your microphone.")
                
        except Exception as e:
            st.error(f"Voice input error: {e}")
    
    def _handle_flow_resumption(self):
        """Handle resuming a flow from proactive message"""
        st.session_state.resume_flow = False
        
        # Add a message to resume the flow with UTC time
        from datetime import timezone
        utc_time = datetime.now(timezone.utc)
        resume_message = {
            "role": "user",
            "content": "Yes, let's continue where we left off.",
            "timestamp": utc_time.isoformat()
        }
        st.session_state.chat_history.append(resume_message)
        
        # Process the resumption
        self._process_user_message("Yes, let's continue where we left off.")
    
    def add_proactive_message(self, message: str):
        """Add a proactive message to the chat"""
        from datetime import timezone
        utc_time = datetime.now(timezone.utc)
        proactive_message = {
            "role": "assistant",
            "content": message,
            "timestamp": utc_time.isoformat(),
            "type": "proactive"
        }
        st.session_state.chat_history.append(proactive_message)
        st.rerun()
    
    def clear_chat_history(self):
        """Clear the chat history"""
        st.session_state.chat_history = []
        st.session_state.current_flow = None
        st.session_state.pending_confirmation = None
        st.rerun()
    
    def export_chat_history(self) -> Dict[str, Any]:
        """Export chat history for download"""
        from datetime import timezone
        utc_time = datetime.now(timezone.utc)
        return {
            "user_id": self.user_id,
            "chat_history": st.session_state.get("chat_history", []),
            "export_timestamp": utc_time.isoformat()
        }
    
    def _stream_response(self, response_text: str, container):
        """Stream the response text with typing effect and auto-scroll"""
        # Split response into words for streaming
        words = response_text.split()
        streamed_text = ""
        
        for i, word in enumerate(words):
            streamed_text += word + " "
            
            # Update every 2-3 words for smooth streaming
            if i % 2 == 0 or i == len(words) - 1:
                # Create HTML with typing indicator (except on last word)
                if i == len(words) - 1:
                    # Final message without typing indicator
                    html_content = f"""
                    <div class="ai-message" id="streaming-message">
                        <b>Noww Club AI</b><br>
                        {streamed_text.strip()}
                    </div>
                    <script>
                    setTimeout(function() {{
                        var element = document.getElementById('streaming-message');
                        if (element) {{
                            element.scrollIntoView({{ behavior: 'smooth', block: 'end' }});
                        }}
                    }}, 50);
                    </script>
                    """
                else:
                    # Streaming message with typing indicator
                    html_content = f"""
                    <div class="ai-message" id="streaming-message">
                        <b>Noww Club AI</b><br>
                        {streamed_text}<span class="typing-indicator">▋</span>
                    </div>
                    <script>
                    setTimeout(function() {{
                        var element = document.getElementById('streaming-message');
                        if (element) {{
                            element.scrollIntoView({{ behavior: 'smooth', block: 'end' }});
                        }}
                    }}, 50);
                    </script>
                    """
                
                container.markdown(html_content, unsafe_allow_html=True)
                time.sleep(0.04)  # Adjust speed for smooth streaming
        
        # Clear the container after streaming is complete
        # This prevents the streamed content from interfering with the main chat display
    
    def _format_ai_response(self, response: str) -> str:
        """Format AI response to ensure proper markdown and styling"""
        # Add line breaks for better readability
        response = re.sub(r'•\s*', '• ', response)  # Clean bullet points
        response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)  # Bold text
        response = re.sub(r'\n\n+', '<br><br>', response)  # Paragraph breaks
        response = re.sub(r'\n', '<br>', response)  # Line breaks
        return response
    
    def _is_vision_board_request(self, message: str) -> bool:
        """Check if the message is requesting a vision board"""
        vision_keywords = [
            'vision board', 'dream board', 'visualize my goals', 'show my future', 
            'create my vision', 'vision', 'dreams visualization', 'goal board',
            'my dreams', 'visualize dreams', 'show my goals', 'future board',
            'destiny', 'aspirations board', 'create vision board'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in vision_keywords)

    def _handle_vision_board_request(self):
        """Handle vision board generation with proper intake flow"""
        try:
            # Check if user has completed intake
            from core.vision_board_intake import VisionBoardIntakeManager
            intake_manager = VisionBoardIntakeManager(
                self.smart_agent.db_manager, 
                self.smart_agent.memory_manager
            )
            
            if not intake_manager.is_intake_complete(self.user_id):
                # Show intake required message
                intake_message = """🎨 **I'd love to create a vision board for you!**

To create the most meaningful and personalized vision board, I need to understand your dreams and aspirations better. 

This involves a quick 10-question intake process that will help me capture your unique vision perfectly.

**Would you like to start the vision board intake?** ✨"""
                
                # Add message to chat
                intake_msg = {
                    "role": "assistant",
                    "content": intake_message,
                    "timestamp": datetime.now().isoformat()
                }
                
                if self.session_manager:
                    self.session_manager.save_message("assistant", intake_message)
                else:
                    st.session_state.chat_history.append(intake_msg)
                
                st.rerun()
                return
            
            # Intake completed - proceed with generation
            self._generate_vision_board_after_intake()
            
        except Exception as e:
            print(f"Error in vision board request handler: {e}")
            error_message = "❌ I encountered an error setting up your vision board. Please try again."
            
            if self.session_manager:
                self.session_manager.save_message("assistant", error_message)
            else:
                error_msg = {
                    "role": "assistant",
                    "content": error_message,
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.chat_history.append(error_msg)
    
    def _generate_vision_board_after_intake(self):
        """Generate vision board after intake is completed"""
        try:
            # Show initial processing message
            initial_message = "🎨 Perfect! Your intake is complete. I'm creating your personalized vision board now..."
            
            # Add initial message to chat
            initial_msg = {
                "role": "assistant",
                "content": initial_message,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.session_manager:
                self.session_manager.save_message("assistant", initial_message)
            else:
                st.session_state.chat_history.append(initial_msg)
            
            # Show processing message
            st.info('🎨 Creating your vision board based on your intake responses... Check the terminal for progress!')
            
            print(f"🎨 Starting vision board generation for user {self.user_id}")
            print("=" * 60)
            
            # Generate the vision board
            vision_generator = self.smart_agent.vision_board_generator
            image_url, template_name = vision_generator.generate_vision_board(self.user_id)
            
            print("=" * 60)
            
            if image_url and template_name:
                # Check if intake was required
                if template_name == "intake_required":
                    error_message = "❌ Please complete the vision board intake first by saying 'Start vision board intake'."
                    
                    error_msg = {
                        "role": "assistant", 
                        "content": error_message,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if self.session_manager:
                        self.session_manager.save_message("assistant", error_message)
                    else:
                        st.session_state.chat_history.append(error_msg)
                        
                    st.error(error_message)
                    st.rerun()
                    return
                
                # Success! Create success message
                success_message = f"""🎉 **Your Vision Board is Ready!**

I've created a beautiful **{template_name}** vision board based on your thoughtful intake responses! This design captures your unique personality, aspirations, and the energy you want to manifest.

✨ **What makes this special:**
- Personalized based on your 10-question intake
- Reflects your specific goals and dreams  
- Matches your personal vibe and energy
- Designed to inspire you daily

Take a moment to really look at it and feel the energy of your future self! 🌟"""
                
                # Add success message
                success_msg = {
                    "role": "assistant",
                    "content": success_message,
                    "timestamp": datetime.now().isoformat()
                }
                
                if self.session_manager:
                    self.session_manager.save_message("assistant", success_message)
                else:
                    st.session_state.chat_history.append(success_msg)
                
                # Add vision board image message
                vision_msg = {
                    "role": "assistant",
                    "content": "vision_board_image",
                    "timestamp": datetime.now().isoformat(),
                    "type": "vision_board",
                    "image_url": image_url,
                    "template_name": template_name
                }
                
                if self.session_manager:
                    try:
                        self.session_manager.save_vision_board_message(
                            image_url, 
                            template_name
                        )
                        print("✅ Vision board saved to session successfully")
                    except Exception as e:
                        print(f"⚠️ Failed to save vision board to session: {e}")
                        # Fallback: add to session state directly
                        if 'messages' in st.session_state:
                            st.session_state.messages.append(vision_msg)
                        else:
                            st.session_state.chat_history.append(vision_msg)
                else:
                    # Legacy mode: add to chat history
                    if hasattr(st.session_state, 'chat_history'):
                        st.session_state.chat_history.append(vision_msg)
                    else:
                        st.session_state.chat_history = [vision_msg]
                
                print(f"✅ Vision board generated successfully: {template_name}")
            
            else:
                # Handle failure
                error_message = "❌ I encountered an issue generating your vision board. Please try again in a moment."
                
                error_msg = {
                    "role": "assistant",
                    "content": error_message,
                    "timestamp": datetime.now().isoformat()
                }
                
                if self.session_manager:
                    self.session_manager.save_message("assistant", error_message)
                else:
                    st.session_state.chat_history.append(error_msg)
                
                print("❌ Vision board generation failed")
            
            # Rerun to display new messages
            st.rerun()
            
        except Exception as e:
            print(f"Error in vision board generation: {e}")
            import traceback
            traceback.print_exc()
            
            error_message = "❌ I encountered an error generating your vision board. Please try again."
            
            if self.session_manager:
                self.session_manager.save_message("assistant", error_message)
            else:
                error_msg = {
                    "role": "assistant",
                    "content": error_message,
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.chat_history.append(error_msg)
                print("❌ Vision board generation failed - no image URL returned")
                error_message = """😔 **Oops! Something went wrong...**

I encountered an issue while creating your vision board. This might be temporary - please try again in a moment!

If the problem persists, you can:
- Try rephrasing your request
- Check your internet connection
- Contact support if needed

Don't worry, I'm here to help you visualize your dreams! ✨"""
                
                error_msg = {
                    "role": "assistant",
                    "content": error_message,
                    "timestamp": datetime.now().isoformat()
                }
                
                if self.session_manager:
                    self.session_manager.save_message("assistant", error_message)
                else:
                    st.session_state.chat_history.append(error_msg)
                
                print("❌ Vision board generation failed")
            
            # Rerun to show results
            st.rerun()
            
        except Exception as e:
            print(f"❌ Error in vision board generation: {e}")
            import traceback
            traceback.print_exc()
            
            # Handle exception
            error_message = f"""😔 **Technical Issue Encountered**

I ran into a technical problem while creating your vision board: {str(e)[:100]}...

Please try again in a moment. If this keeps happening, let me know and I'll help you another way! ✨"""
            
            error_msg = {
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.session_manager:
                self.session_manager.save_message("assistant", error_message)
            else:
                st.session_state.chat_history.append(error_msg)
            
            st.rerun()

    def _display_vision_board(self, image_url: str, template_name: str):
        """Display the vision board image with download option"""
        try:
            # Create a beautiful container for the vision board
            st.markdown("""
            <div style="margin: 20px 0; padding: 20px; border: 2px solid #667eea; border-radius: 15px; 
                        background: linear-gradient(135deg, #f8f9ff 0%, #e8f0fe 100%); text-align: center;">
                <h3 style="color: #667eea; margin-bottom: 15px;">🎨 Your Personalized Vision Board</h3>
                <p style="color: #2c3e50; margin-bottom: 20px;">Created just for you based on your profile and aspirations!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Download and display image with controlled sizing
            if image_url.startswith('data:image'):
                # Handle base64 data URL from GPT-Image-1
                base64_data = image_url.split(',')[1]
                image_bytes = base64.b64decode(base64_data)
                image = Image.open(BytesIO(image_bytes))
            else:
                # Handle regular URL from DALL-E or other sources
                response = requests.get(image_url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            
            # Create columns to control image width and center it
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col2:  # Center column with controlled width
                # Display the image with optimal sizing
                st.image(
                    image, 
                    caption=f"Your Personalized Vision Board - {template_name}",
                    use_container_width=True
                )
            
            # Download button centered
            img_buffer = BytesIO()
            image.save(img_buffer, format='PNG', optimize=True, quality=95)  # Enhanced quality
            img_buffer.seek(0)
            
            # Center the download button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.download_button(
                    label="💾 Download Your Vision Board",
                    data=img_buffer.getvalue(),
                    file_name=f"vision_board_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    help="Click to download your vision board as a PNG image",
                    use_container_width=True
                )
            
        except Exception as e:
            st.error(f"Error displaying vision board: {e}")
