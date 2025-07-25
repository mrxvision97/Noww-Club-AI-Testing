import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from core.user_profile import UserProfileManager
from utils.notifications import NotificationManager
from ui.analytics import AnalyticsDashboard

class SidebarInterface:
    def __init__(self, profile_manager: UserProfileManager, notification_manager: NotificationManager, user_id: str, action_handler=None):
        self.profile_manager = profile_manager
        self.notification_manager = notification_manager
        self.user_id = user_id
        self.analytics = AnalyticsDashboard(profile_manager, user_id)
        self.action_handler = action_handler
    
    def render(self):
        """Render the modern sidebar interface."""
        
        with st.sidebar:
            # Add modern CSS styling for sidebar
            st.markdown("""
            <style>
            /* Import Inter font */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Sidebar styling */
            .css-1d391kg {
                background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            }
            
            /* Modern header styling */
            .sidebar-header {
                text-align: center;
                padding: 20px 0;
                margin-bottom: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                margin: 0 -1rem 25px -1rem;
                color: white;
            }
            
            .sidebar-header h2 {
                font-family: 'Inter', sans-serif;
                font-size: 1.4rem;
                font-weight: 700;
                margin: 0;
                color: white;
            }
            
            .sidebar-header p {
                font-family: 'Inter', sans-serif;
                font-size: 0.85rem;
                margin: 5px 0 0 0;
                opacity: 0.9;
                color: white;
            }
            
            /* Section headers */
            .sidebar-section h5 {
                font-family: 'Inter', sans-serif;
                font-size: 1rem;
                font-weight: 600;
                color: #374151;
                margin: 20px 0 12px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid #e5e7eb;
            }
            
            /* Metric cards */
            .metric-card {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
                margin: 8px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: all 0.2s ease;
            }
            
            .metric-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateY(-1px);
            }
            
            .metric-card h6 {
                font-family: 'Inter', sans-serif;
                font-size: 0.8rem;
                color: #6b7280;
                margin: 0 0 4px 0;
                font-weight: 500;
            }
            
            .metric-card .metric-value {
                font-family: 'Inter', sans-serif;
                font-size: 1.5rem;
                font-weight: 700;
                color: #1f2937;
                margin: 0;
            }
            
            /* Info cards styling */
            .stInfo {
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important;
                border: 1px solid #0ea5e9 !important;
                border-radius: 12px !important;
                margin: 8px 0 !important;
            }
            
            /* Button styling */
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
                transition: all 0.2s ease;
                width: 100%;
                margin: 8px 0;
            }
            
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }
            
            /* Expander styling */
            .streamlit-expanderHeader {
                background: #f8fafc;
                border-radius: 12px;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Modern header
            st.markdown("""
            <div class="sidebar-header">
                <h2>✨ Noww Club AI</h2>
                <p>Your personal growth companion</p>
            </div>
            """, unsafe_allow_html=True)
            
            # User Profile Section
            self._render_modern_profile_section()
            
            # Active Habits & Goals
            self._render_active_habits()
            self._render_active_goals()

            # Mood Tracking
            self._render_mood_section()
            
            # Lifestyle Actions (when user has started chatting)
            if st.session_state.get('messages') or st.session_state.get('chat_history'):
                self._render_lifestyle_actions()
            
            # Settings & Actions
            self._render_modern_settings_section()

    def _render_modern_profile_section(self):
        """Renders a modern 'Your Profile' section."""
        st.markdown('<div class="sidebar-section"><h5>👤 Your Journey</h5></div>', unsafe_allow_html=True)
        
        profile = self.profile_manager.get_user_profile(self.user_id)
        
        # Conversations metric
        st.markdown("""
        <div class="metric-card">
            <h6>Conversations</h6>
            <div class="metric-value">{}</div>
        </div>
        """.format(len(st.session_state.get("chat_history", []))), unsafe_allow_html=True)
        
        # Journey status
        st.markdown("""
        <div class="metric-card">
            <h6>Journey Status</h6>
            <div class="metric-value">🌱 Growing</div>
        </div>
        """, unsafe_allow_html=True)

    def _render_active_habits(self):
        """Renders a modern 'Active Habits' section."""
        st.markdown('<div class="sidebar-section"><h5>🌿 Active Habits</h5></div>', unsafe_allow_html=True)
        habits = self.profile_manager.get_user_profile(self.user_id).get("habits", [])
        if not habits:
            st.info("💡 Ready to build amazing habits? Start a conversation to create your first one!")
        else:
            for habit in habits[:3]: # Show top 3
                st.info(f"✅ {habit['title']}")

    def _render_active_goals(self):
        """Renders a modern 'Active Goals' section.""" 
        st.markdown('<div class="sidebar-section"><h5>🎯 Active Goals</h5></div>', unsafe_allow_html=True)
        goals = self.profile_manager.get_user_profile(self.user_id).get("goals", [])
        if not goals:
            st.info("🚀 Let's set some inspiring goals! Chat with me to get started.")
        else:
            for goal in goals[:3]: # Show top 3
                st.info(f"🎯 {goal['title']}")

    def _render_mood_section(self):
        """Renders a modern 'Recent Moods' section."""
        st.markdown('<div class="sidebar-section"><h5>😊 Mood Journey</h5></div>', unsafe_allow_html=True)
        moods = self.profile_manager.db_manager.get_mood_entries(self.user_id, limit=3)
        if not moods:
            st.info("💭 How are you feeling today? Share your mood with me anytime!")
        else:
            for mood in moods:
                emoji = self._get_mood_emoji(mood['mood_score'])
                date_str = datetime.fromisoformat(mood['timestamp']).strftime('%b %d')
                st.info(f"{emoji} {mood['mood_score']}/5 on {date_str}")

    def _render_lifestyle_actions(self):
        """Renders lifestyle action buttons in the sidebar when user has started chatting."""
        st.markdown('<div class="sidebar-section"><h5>✨ Lifestyle Actions</h5></div>', unsafe_allow_html=True)
        
        # Create compact buttons for sidebar
        if st.button("💭 Brainstorm", key="sidebar_brainstorm", use_container_width=True, help="Brainstorm ideas and explore creativity"):
            if self.action_handler:
                self.action_handler("reflect_talk")
        
        if st.button("📝 Journal", key="sidebar_journal", use_container_width=True, help="Journal thoughts and reflect on your day"):
            if self.action_handler:
                self.action_handler("habit_reminder")
        
        if st.button("🎯 Goals", key="sidebar_goals", use_container_width=True, help="Set and discuss your goals"):
            if self.action_handler:
                self.action_handler("mindful_rituals")
        
        if st.button("🎨 Vision Board", key="sidebar_vision", use_container_width=True, help="Create a personalized vision board"):
            if self.action_handler:
                self.action_handler("vision_board")

    def _render_modern_settings_section(self):
        """Renders modern settings and actions."""
        st.markdown('<div class="sidebar-section"><h5>⚙️ Preferences</h5></div>', unsafe_allow_html=True)
        
        with st.expander("🔔 Notification Settings"):
            preferences = self.profile_manager.get_notification_preferences(self.user_id)
            
            reminders = st.checkbox("Daily Reminders", preferences.get("reminders_enabled", True))
            mood_checkins = st.checkbox("Mood Check-ins", preferences.get("mood_check_ins", True))
            
            if st.button("💾 Save Settings"):
                new_prefs = {
                    "reminders_enabled": reminders,
                    "mood_check_ins": mood_checkins,
                }
                self.profile_manager.update_notification_preferences(self.user_id, new_prefs)
                st.success("✅ Settings saved!")
        
        # Quick Actions
        st.markdown('<div class="sidebar-section"><h5>⚡ Quick Actions</h5></div>', unsafe_allow_html=True)
        
        if st.button("📊 View Analytics"):
            st.session_state.show_analytics = True
            st.rerun()
        
        if st.button("🔄 Clear Chat"):
            st.session_state.chat_history = []
            st.success("Chat cleared!")
            st.rerun()

    def _get_mood_emoji(self, mood_score: float) -> str:
        """Get emoji for mood score"""
        if mood_score >= 4.5:
            return "😄"
        elif mood_score >= 3.5:
            return "😊"
        elif mood_score >= 2.5:
            return "😐"
        elif mood_score >= 1.5:
            return "😔"
        else:
            return "😢"
    
    def render_analytics_modal(self):
        """Render analytics modal if requested"""
        if st.session_state.get("show_analytics", False):
            st.session_state.show_analytics = False
            
            # Create a new page/modal for analytics
            st.subheader("📈 Analytics Dashboard")
            
            try:
                self.analytics.render_full_dashboard()
            except Exception as e:
                st.error(f"Error loading analytics: {str(e)}")
            
            if st.button("Close Analytics"):
                st.rerun()
