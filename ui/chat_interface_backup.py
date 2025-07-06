import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time
import re
# Smart agent handles all processing
from core.memory import MemoryManager

class ChatInterface:
    def __init__(self, smart_agent, memory_manager: MemoryManager, user_id: str, voice_handler=None, session_manager=None):
        self.smart_agent = smart_agent
        self.memory_manager = memory_manager
        self.user_id = user_id
        self.voice_handler = voice_handler
        self.session_manager = session_manager
    
    def _get_ist_time(self, timestamp=None):
        """Convert timestamp to IST (Indian Standard Time)"""
        if timestamp is None:
            # Get current UTC time and convert to IST
            from datetime import timezone
            utc_now = datetime.now(timezone.utc)
            ist_timestamp = utc_now + timedelta(hours=5, minutes=30)
            return ist_timestamp.replace(tzinfo=None)  # Remove timezone info for consistency
        
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        # If timestamp has timezone info, convert to UTC first
        if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
            # Convert to UTC, then to IST
            utc_timestamp = timestamp.utctimetuple()
            utc_datetime = datetime(*utc_timestamp[:6])
            ist_timestamp = utc_datetime + timedelta(hours=5, minutes=30)
        else:
            # Assume it's UTC and convert to IST
            ist_timestamp = timestamp + timedelta(hours=5, minutes=30)
        
        return ist_timestamp
    
    def render(self):
        """Render the chat interface"""
        # Use session manager messages if available, otherwise fallback to legacy
        if self.session_manager:
            messages = st.session_state.get('messages', [])
        else:
            # Legacy support - initialize chat history if not exists
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            messages = st.session_state.chat_history
        
        # Display chat history
        self._display_chat_history(messages)
        
        # Add lifestyle concierge tabs before the chat input
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
            if self.session_manager:
                messages = st.session_state.get('messages', [])
            else:
                messages = st.session_state.get('chat_history', [])
        
        # Add custom CSS for chat bubbles with enhanced styling
        st.markdown("""
        <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            max-height: 500px;
            overflow-y: auto;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 15px;
            background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .user-message {
            align-self: flex-end;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 18px;
            border-radius: 25px 25px 8px 25px;
            max-width: 75%;
            margin-left: auto;
            word-wrap: break-word;
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
            animation: slideInRight 0.4s ease-out;
            font-weight: 500;
        }
        
        .ai-message {
            align-self: flex-start;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            color: #2c3e50;
            padding: 15px 20px;
            border-radius: 25px 25px 25px 8px;
            max-width: 85%;
            margin-right: auto;
            word-wrap: break-word;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
            animation: slideInLeft 0.4s ease-out;
            line-height: 1.7;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .ai-message b {
            color: #667eea;
            font-size: 1.1em;
            margin-bottom: 8px;
            display: block;
        }
        
        .ai-message ul, .ai-message ol {
            margin: 10px 0;
            padding-left: 20px;
        }
        
        .ai-message li {
            margin: 6px 0;
            line-height: 1.6;
        }
        
        .ai-message h3, .ai-message h4 {
            color: #2c3e50;
            margin: 12px 0 6px 0;
        }
        
        .proactive-message {
            align-self: flex-start;
            background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
            color: #2d5a2d;
            padding: 12px 18px;
            border: 2px solid #4CAF50;
            border-radius: 25px 25px 25px 8px;
            max-width: 75%;
            margin-right: auto;
            word-wrap: break-word;
            animation: bounceIn 0.6s ease-out;
            box-shadow: 0 3px 10px rgba(76, 175, 80, 0.2);
        }
        
        .typing-indicator {
            animation: blink 1s infinite;
            color: #667eea;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        @keyframes slideInRight {
            from { transform: translateX(30px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideInLeft {
            from { transform: translateX(-30px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .timestamp {
            font-size: 0.85em;
            color: #888;
            text-align: center;
            margin: 8px 0;
            font-style: italic;
        }
        
        /* Scrollbar styling */
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 10px;
        }
        
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create chat container
        if messages:
            chat_html = '<div class="chat-container">'
            
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
                    else:
                        # Display AI message with proper HTML formatting
                        chat_html += f'<div class="ai-message"><b>Noww Club AI</b><br>{content}</div>'
            
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
        
        else:
            # Welcome message with better formatting
            st.markdown("""
            <div class="chat-container">
                <div class="ai-message">
                    <b>Noww Club AI</b><br>
                    🌟 <strong>Hello! I'm Noww Club AI</strong> - your digital bestie with advanced memory and web search capabilities!
                    <br><br>
                    <strong>Here's how I can help you:</strong>
                    <br>• 🎯 <strong>Building meaningful habits</strong> and tracking progress
                    <br>• 😊 <strong>Tracking your mood</strong> and well-being journey
                    <br>• 🚀 <strong>Setting and achieving goals</strong> with personalized plans
                    <br>• ⏰ <strong>Managing daily reminders</strong> and important tasks
                    <br>• 🔍 <strong>Real-time web search</strong> for any questions
                    <br>• 💭 <strong>Remembering our conversations</strong> to provide better support
                    <br><br>
                    💡 <strong>What would you like to work on today?</strong> I'm excited to help! 🌈
                </div>
            </div>
            """, unsafe_allow_html=True)
    
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
        if user_input := st.chat_input("💬 Ask me anything, share your thoughts, or request web searches..."):
            self._process_user_message(user_input.strip())
    
    def _render_lifestyle_concierge_tabs(self):
        """Render the lifestyle concierge tabs with icons and descriptions"""
        
        # Create 4 columns for the tabs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button(
                "💭\nReflect / Talk", 
                use_container_width=True,
                help="Check in on how you're feeling or reflect on your day",
                key="reflect_talk_btn"
            ):
                self._handle_lifestyle_action("reflect_talk")
        
        with col2:
            if st.button(
                "🔔\nHabit / Reminder", 
                use_container_width=True,
                help="Get gentle nudges for positive habits",
                key="habit_reminder_btn"
            ):
                self._handle_lifestyle_action("habit_reminder")
        
        with col3:
            if st.button(
                "🧘‍♀️\nMindful Rituals", 
                use_container_width=True,
                help="Embrace calm and intentional moments daily",
                key="mindful_rituals_btn"
            ):
                self._handle_lifestyle_action("mindful_rituals")
        
        with col4:
            if st.button(
                "🔍\nDiscover", 
                use_container_width=True,
                help="Find curated brands, experiences, and community",
                key="discover_btn"
            ):
                self._handle_lifestyle_action("discover")
        
        # Enhanced styling for the lifestyle concierge buttons
        st.markdown("""
        <style>
        /* Lifestyle Concierge Button Styling */
        div[data-testid="column"] .stButton > button {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border: 2px solid #e9ecef;
            border-radius: 20px;
            color: #495057;
            font-weight: 600;
            padding: 18px 12px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            height: 85px;
            font-size: 14px;
            line-height: 1.3;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            position: relative;
            overflow: hidden;
        }
        
        div[data-testid="column"] .stButton > button:hover {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: #667eea;
            color: white;
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
        }
        
        div[data-testid="column"] .stButton > button:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
            outline: none;
        }
        
        div[data-testid="column"] .stButton > button:active {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        }
        
        /* Add a subtle animation effect */
        div[data-testid="column"] .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }
        
        div[data-testid="column"] .stButton > button:hover::before {
            left: 100%;
        }
        
        /* Lifestyle Concierge section container */
        .lifestyle-concierge-container {
            margin: 10px 0;
            padding: 15px;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 20px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 15px rgba(0,0,0,0.06);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _handle_lifestyle_action(self, action_type: str):
        """Handle lifestyle concierge actions"""
        action_config = {
            "reflect_talk": {
                "prompt": "I'd like to reflect on my day and check in on how I'm feeling. Can you help me process my thoughts and emotions with thoughtful questions and guidance?",
                "success_message": "✨ Reflection & Talk mode activated! Let's explore your thoughts together.",
                "emoji": "💭"
            },
            "habit_reminder": {
                "prompt": "I want to work on building positive habits and need gentle reminders. Can you help me set up a personalized habit tracking system and provide encouraging nudges?",
                "success_message": "✨ Habit & Reminder mode activated! Let's build positive routines together.",
                "emoji": "🔔"
            },
            "mindful_rituals": {
                "prompt": "I'm interested in incorporating mindful rituals and intentional moments into my daily routine. Can you guide me through calming practices and suggest mindfulness techniques?",
                "success_message": "✨ Mindful Rituals mode activated! Let's embrace calm and intentional moments.",
                "emoji": "🧘‍♀️"
            },
            "discover": {
                "prompt": "I'd like to discover new brands, experiences, and community connections that align with my lifestyle preferences. Can you recommend curated options based on my interests?",
                "success_message": "✨ Discover mode activated! Let's explore new experiences together.",
                "emoji": "🔍"
            }
        }
        
        if action_type in action_config:
            config = action_config[action_type]
            
            # Add a visual indication with the specific emoji and message
            st.success(f"{config['emoji']} {config['success_message']}")
            
            # Process the predefined prompt
            self._process_user_message(config['prompt'])
            
            # Brief pause and rerun
            time.sleep(0.5)
            st.rerun()
    
    def _process_user_message(self, message: str):
        """Process user message through the state graph with streaming"""
        # Add user message to chat history with current UTC time
        from datetime import timezone
        utc_time = datetime.now(timezone.utc)
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": utc_time.isoformat()
        }
        
        # Save message using session manager if available
        if self.session_manager:
            self.session_manager.save_message("user", message)
        else:
            # Legacy: add to chat history
            st.session_state.chat_history.append(user_message)
        
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
                
                # Save message using session manager if available
                if self.session_manager:
                    self.session_manager.save_message("assistant", formatted_response)
                else:
                    # Legacy: add to chat history
                    st.session_state.chat_history.append(ai_message)
                
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
                st.session_state.chat_history.append(ai_message)
        
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
        """Stream the response text with typing effect"""
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
                    <div class="ai-message">
                        <b>Noww Club AI</b><br>
                        {streamed_text.strip()}
                    </div>
                    """
                else:
                    # Streaming message with typing indicator
                    html_content = f"""
                    <div class="ai-message">
                        <b>Noww Club AI</b><br>
                        {streamed_text}<span class="typing-indicator">▋</span>
                    </div>
                    """
                
                container.markdown(html_content, unsafe_allow_html=True)
                time.sleep(0.04)  # Adjust speed for smooth streaming
    
    def _format_ai_response(self, response: str) -> str:
        """Format AI response to ensure proper markdown and styling"""
        # Add line breaks for better readability
        response = re.sub(r'•\s*', '• ', response)  # Clean bullet points
        response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)  # Bold text
        response = re.sub(r'\n\n+', '<br><br>', response)  # Paragraph breaks
        response = re.sub(r'\n', '<br>', response)  # Line breaks
        return response
