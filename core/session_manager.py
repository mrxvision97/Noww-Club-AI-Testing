import streamlit as st
import os
from typing import Optional, Dict, Any
from datetime import datetime
import json

class SessionManager:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.session_key = "user_session"
    
    def initialize_session(self):
        """Initialize session state variables"""
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
    
    def login_user(self, user_info: Dict[str, Any]):
        """Log in a user and set session state"""
        st.session_state.authenticated = True
        st.session_state.user_id = user_info['user_id']
        st.session_state.user_info = user_info
        st.session_state.show_auth = False
        
        # Load user's chat sessions
        self.load_user_chat_sessions()
        
        # Create a new chat session if none exists
        if not st.session_state.chat_sessions:
            self.create_new_chat_session()
    
    def logout_user(self):
        """Log out the current user"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_info = None
        st.session_state.current_chat_session = None
        st.session_state.chat_sessions = []
        st.session_state.messages = []
        st.session_state.show_auth = True
        
        # Clear other session variables
        for key in list(st.session_state.keys()):
            if key not in ['authenticated', 'user_id', 'user_info', 'current_chat_session', 'chat_sessions', 'messages', 'show_auth']:
                if key.startswith('user_') or key.startswith('chat_'):
                    del st.session_state[key]
    
    def load_user_chat_sessions(self):
        """Load chat sessions for the current user"""
        if st.session_state.user_id:
            sessions = self.auth_manager.get_user_chat_sessions(st.session_state.user_id)
            st.session_state.chat_sessions = sessions
            
            # Set current chat session to the most recent one
            if sessions and not st.session_state.current_chat_session:
                st.session_state.current_chat_session = sessions[0]['id']
                self.load_chat_history(sessions[0]['id'])
    
    def create_new_chat_session(self, session_name: str = None):
        """Create a new chat session"""
        if not st.session_state.user_id:
            return None
        
        if not session_name:
            session_name = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        session_id = self.auth_manager.create_chat_session(st.session_state.user_id, session_name)
        
        if session_id:
            # Reload chat sessions
            self.load_user_chat_sessions()
            
            # Switch to new session
            st.session_state.current_chat_session = session_id
            st.session_state.messages = []
            
            return session_id
        return None
    
    def switch_chat_session(self, session_id: int):
        """Switch to a different chat session"""
        if session_id != st.session_state.current_chat_session:
            st.session_state.current_chat_session = session_id
            self.load_chat_history(session_id)
    
    def load_chat_history(self, session_id: int):
        """Load chat history for a specific session"""
        if st.session_state.user_id:
            messages = self.auth_manager.get_chat_history(st.session_state.user_id, session_id)
            
            # Convert to Streamlit chat format
            st.session_state.messages = []
            for msg in messages:
                if msg['message_type'] in ['user', 'assistant']:
                    st.session_state.messages.append({
                        'role': msg['message_type'],
                        'content': msg['content'],
                        'timestamp': msg['timestamp']
                    })
    
    def save_message(self, role: str, content: str, metadata: Dict = None):
        """Save a message to the current chat session"""
        if st.session_state.user_id and st.session_state.current_chat_session:
            success = self.auth_manager.save_message(
                st.session_state.user_id,
                st.session_state.current_chat_session,
                role,
                content,
                metadata
            )
            
            if success:
                # Add to session messages
                st.session_state.messages.append({
                    'role': role,
                    'content': content,
                    'timestamp': datetime.now().isoformat()
                })
            
            return success
        return False
    
    def save_vision_board_message(self, image_url: str, template_name: str):
        """Save a vision board message to the current chat session"""
        if st.session_state.user_id and st.session_state.current_chat_session:
            # Create vision board message
            vision_message = {
                "role": "assistant",
                "content": "vision_board_image",
                "timestamp": datetime.now().isoformat(),
                "type": "vision_board",
                "image_url": image_url,
                "template_name": template_name
            }
            
            # Save to database via auth manager
            success = self.auth_manager.save_message(
                st.session_state.user_id,
                st.session_state.current_chat_session,
                "assistant",
                "vision_board_image",
                metadata={
                    "type": "vision_board",
                    "image_url": image_url,
                    "template_name": template_name
                }
            )
            
            if success:
                # Add to current session messages
                st.session_state.messages.append(vision_message)
            
            return success
        return False
    
    def get_current_user_profile_id(self) -> Optional[str]:
        """Get the current user's profile ID for compatibility with existing code"""
        if st.session_state.user_id:
            return f"user_{st.session_state.user_id}"
        return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        return st.session_state.get('user_info')
    
    def get_current_chat_session(self) -> Optional[int]:
        """Get current chat session ID"""
        return st.session_state.get('current_chat_session')
    
    def get_chat_sessions(self) -> list:
        """Get all chat sessions for current user"""
        return st.session_state.get('chat_sessions', [])
    
    def rename_chat_session(self, session_id: int, new_name: str):
        """Rename a chat session"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.auth_manager.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE chat_sessions 
                SET session_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (new_name, session_id, st.session_state.user_id))
            
            conn.commit()
            conn.close()
            
            # Reload chat sessions
            self.load_user_chat_sessions()
            
            return True
        except Exception as e:
            return False
    
    def delete_chat_session(self, session_id: int):
        """Delete a chat session"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.auth_manager.db_manager.db_path)
            cursor = conn.cursor()
            
            # Delete conversations in this session
            cursor.execute('''
                DELETE FROM conversations 
                WHERE chat_session_id = ? AND user_id = ?
            ''', (session_id, st.session_state.user_id))
            
            # Delete chat session
            cursor.execute('''
                DELETE FROM chat_sessions 
                WHERE id = ? AND user_id = ?
            ''', (session_id, st.session_state.user_id))
            
            conn.commit()
            conn.close()
            
            # If this was the current session, switch to another one
            if st.session_state.current_chat_session == session_id:
                self.load_user_chat_sessions()
                if st.session_state.chat_sessions:
                    st.session_state.current_chat_session = st.session_state.chat_sessions[0]['id']
                    self.load_chat_history(st.session_state.chat_sessions[0]['id'])
                else:
                    self.create_new_chat_session()
            else:
                self.load_user_chat_sessions()
            
            return True
        except Exception as e:
            return False
