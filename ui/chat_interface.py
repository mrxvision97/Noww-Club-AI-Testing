import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional
import time
import re
# Smart agent handles all processing
from core.memory import MemoryManager

class ChatInterface:
    def __init__(self, smart_agent, memory_manager: MemoryManager, user_id: str, voice_handler=None):
        self.smart_agent = smart_agent
        self.memory_manager = memory_manager
        self.user_id = user_id
        self.voice_handler = voice_handler
    
    def render(self):
        """Render the chat interface"""
        # Initialize chat history if not exists
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        self._display_chat_history()
        
        # Chat input
        self._render_chat_input()
        
        # Handle flow resumption
        if st.session_state.get("resume_flow"):
            self._handle_flow_resumption()
    
    def _display_chat_history(self):
        """Display the conversation history with styled bubbles"""
        
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
        if st.session_state.chat_history:
            chat_html = '<div class="chat-container">'
            
            for i, message in enumerate(st.session_state.chat_history):
                # Add timestamp for first message or messages more than 5 minutes apart
                if i == 0 or self._should_show_timestamp(i):
                    timestamp = message.get("timestamp", datetime.now())
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    chat_html += f'<div class="timestamp">{timestamp.strftime("%I:%M %p")}</div>'
                
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
    
    def _should_show_timestamp(self, index: int) -> bool:
        """Determine if timestamp should be shown"""
        if index == 0:
            return True
        
        current_msg = st.session_state.chat_history[index]
        prev_msg = st.session_state.chat_history[index - 1]
        
        current_time = current_msg.get("timestamp")
        prev_time = prev_msg.get("timestamp")
        
        if not current_time or not prev_time:
            return False
        
        if isinstance(current_time, str):
            current_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
        if isinstance(prev_time, str):
            prev_time = datetime.fromisoformat(prev_time.replace('Z', '+00:00'))
        
        # Show timestamp if more than 5 minutes apart
        return (current_time - prev_time).seconds > 300
    
    def _render_chat_input(self):
        """Render the chat input area using st.chat_input for Enter-to-send."""
        if user_input := st.chat_input("💬 Ask me anything, share your thoughts, or request web searches..."):
            self._process_user_message(user_input.strip())
    
    def _process_user_message(self, message: str):
        """Process user message through the state graph with streaming"""
        # Add user message to chat history
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
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
                
                # Add AI response to chat history
                ai_message = {
                    "role": "assistant",
                    "content": formatted_response,
                    "timestamp": datetime.now().isoformat()
                }
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
                
                # Add fallback response
                ai_message = {
                    "role": "assistant",
                    "content": "I'm sorry, I encountered an error processing your message. Please try again.",
                    "timestamp": datetime.now().isoformat()
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
        
        # Add a message to resume the flow
        resume_message = {
            "role": "user",
            "content": "Yes, let's continue where we left off.",
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.chat_history.append(resume_message)
        
        # Process the resumption
        self._process_user_message("Yes, let's continue where we left off.")
    
    def add_proactive_message(self, message: str):
        """Add a proactive message to the chat"""
        proactive_message = {
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat(),
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
        return {
            "user_id": self.user_id,
            "chat_history": st.session_state.get("chat_history", []),
            "export_timestamp": datetime.now().isoformat()
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
